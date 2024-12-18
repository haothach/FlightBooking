import hashlib
import string

from flask import render_template, request, redirect,flash

import dao
from app import app, login, db
from flask_login import login_user, logout_user
from app.models import UserRole, Customer, Gender, Flight, Airplane
from datetime import datetime


@app.route("/", methods=["GET", "POST"])
def index():

    provinces = dao.load_province()
    departure = request.args.get('departure')
    destination = request.args.get('destination')

    return render_template('index.html', provinces=provinces)


@app.route("/search")
def search():
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure_date')
    passenger = request.args.get('passenger')
    time_range = request.args.get('time_range')
    arrival_time_range = request.args.get('arrival_time_range')
    # Lấy danh sách chuyến bay
    flights = dao.load_flights(departure, destination, departure_date)

    formatted_date = datetime.strptime(departure_date, '%Y-%m-%d').strftime('%d/%m/%Y')


    # Lọc theo giờ cất cánh (nếu có)
    if time_range:
        start, end = map(int, time_range.split('-'))
        flights = [
            flight for flight in flights
            if start <= flight['departure_time'].hour < end
        ]

    # Lọc theo giờ hạ cánh (nếu có)
    if arrival_time_range:
        start, end = map(int, arrival_time_range.split('-'))
        flights = [
            flight for flight in flights
            if start <= flight['arrival_time'].hour < end
        ]

    # Kiểm tra ngày chọn có trước ngày hiện tại không
    # departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
    # today = datetime.now().date()
    # if departure_date < today:
    #     flash("Ngày đi không được trước ngày hôm nay!", "danger")
    #     return redirect('/')
    #
    # # Kiểm tra chọn điểm đi và điểm đến chưa
    # if not departure or not destination:
    #     flash("Vui lòng chọn điểm đi và điểm đến!", "danger")
    #     return redirect('/')

    return render_template('search.html', departure=departure, destination=destination,
                           departure_date=formatted_date, passenger=passenger, flights=flights)


@app.route("/register", methods=['get', 'post'])
def register_view():
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not password.__eq__(confirm):
            flash("Mật khẩu không khớp", "danger")
        else:
            data = request.form.copy()
            del data['confirm']
            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)

            return redirect('/login')

    return render_template('register.html')


@app.route("/login", methods=['post', 'get'])
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            if user.user_role == UserRole.ADMIN:
                return redirect('/admin')

            return redirect('/')
    return render_template("login.html")


@app.route("/login-admin", methods=['post'])
def login_admin_view():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if user:
        login_user(user)
    return redirect('/admin')


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/booking')
def book_tickets():
    passenger = int(request.args.get('passenger', 1))
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure_date')
    flight_time = request.args.get('flight_time')
    departure_time = request.args.get('departure_time')
    arrival_time = request.args.get('arrival_time')
    price = int(request.args.get('price'))
    ticket_class = request.args.get('class').capitalize()

    formatted_price = "{:,.0f}".format(price).replace(',', '.')

    total = price * passenger
    formatted_total = "{:,.0f}".format(total).replace(',', '.')

    return render_template('booking.html', departure=departure, destination=destination, passenger=passenger,
                           departure_date=departure_date, flight_time=flight_time, departure_time=departure_time, arrival_time=arrival_time,
                           price=formatted_price, ticket_class=ticket_class, total=formatted_total)


@app.route('/add_customer', methods=['POST'])
def add_customer():

    # Xử lý từng hành khách
    for p in range(int(request.form.get('passenger_count'))):  # Dùng hidden input để truyền số lượng
        name = request.form.get(f'passenger_name_{p}')
        birth_date = request.form.get(f'passenger_birth_{p}')
        gender = request.form.get(f'passenger_gender_{p}')

        # Chuyển đổi ngày sinh về định dạng datetime
        birthday = datetime.strptime(birth_date, '%Y-%m-%d').date()

        # Tạo đối tượng Customer
        customer = Customer(
            name=name.split(" ", 1)[-1],  # Lấy tên
            last_name=name.split(" ", 1)[0],  # Lấy họ
            gender=Gender.Mr if gender.__eq__('Male') else Gender.Ms,  # Map giá trị
            birthday=birthday
        )

        # Thêm vào session
        db.session.add(customer)

        # Lưu thay đổi vào DB
    db.session.commit()

    return redirect('/')  # Trỏ về trang tóm tắt chuyến bay hoặc thanh toán


@app.route('/schedule', methods=['GET', 'POST'])
def flight_schedule():
    flightcodes = dao.load_flight()
    airports = dao.load_airport()
    if request.method == 'POST':
        flight_code = request.form.get('flight_code')
        flight = Flight.query.get(flight_code)
        airplane = Airplane.query.get(flight.airplane_id)

        bussiness_seats = airplane.business_class_seat_size
        ecnomic_seats = airplane.economy_class_seat_size
        return render_template('schedule.html', flightcodes=flightcodes, airports=airports,
                               bussiness_seats=bussiness_seats, ecnomic_seats=ecnomic_seats, flight_code=flight_code)

    return render_template('schedule.html', flightcodes=flightcodes, airports=airports)



if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
