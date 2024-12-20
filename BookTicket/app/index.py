import hashlib
import string

from flask import render_template, request, redirect, flash, jsonify

import dao
from app import app, login, db
from flask_login import login_user, logout_user
from app.models import (UserRole, Customer, Gender, Flight, Airplane, Ticket, SeatAssignment, Seat, IntermediateAirport,
                        FlightRoute, FlightSchedule, Receipt, ReceiptDetail)
from flask_login import login_user, logout_user, current_user, login_required
from app.models import UserRole, Customer, Gender, TicketClass
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
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            if user.user_role == UserRole.ADMIN:
                return redirect('/admin')
            elif user.user_role == UserRole.STAFF:
                return redirect('/staff')
            next_url = request.form.get('next')
            # Xử lý nếu next_url không tồn tại hoặc không hợp lệ
            if not next_url or next_url == '/':
                next_url = '/'
            return redirect(next_url)
        return redirect('/login')
    return render_template("login.html")


@app.route("/login-admin", methods=['post'])
def login_admin_view():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if user:
        login_user(user)
    return redirect('/admin')

@app.route("/staff")
def staff_view():
    return render_template("staff.html")

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    # Gửi thông báo thành công
    flash('Yêu cầu hỗ trợ của bạn đã được gửi thành công!', 'success')
    return redirect('/contact')

@app.route('/contact')
def contact_view():
    return render_template('contact.html')

@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/booking')
def book_tickets():
    # Lấy tham số từ URL
    passenger = int(request.args.get('passenger', 1))
    flight_id = request.args.get('flight_id')
    seat_class = request.args.get('class', '')  # Ví dụ: Business_Class
    departure_date = request.args.get('departure_date')
    flight_time = request.args.get('flight_time')
    departure_time = request.args.get('departure_time')
    arrival_time = request.args.get('arrival_time')
    price = int(request.args.get('price'))

    # Format giá vé
    formatted_price = "{:,.0f}".format(price).replace(',', '.')

    # Tính tổng tiền
    total = price * passenger
    formatted_total = "{:,.0f}".format(total).replace(',', '.')

    # Chuyển đổi seat_class từ chuỗi sang Enum
    if seat_class not in TicketClass.__members__:
        return "Invalid seat class provided.", 400
    seat_class_enum = TicketClass[seat_class]

    # Lấy danh sách ghế trống dựa trên flight_id và seat_class
    available_seats = dao.get_available_seats(flight_id, seat_class_enum)
    if not available_seats:
        return "No available seats for the selected class.", 404

    # Lấy thông tin chuyến bay
    flight = dao.get_flight_by_id(flight_id)
    if not flight:
        return "Flight not found.", 404

    # Render template booking.html
    return render_template(
        'booking.html',
        passenger=passenger,
        departure_date=departure_date,
        flight_time=flight_time,
        departure_time=departure_time,
        arrival_time=arrival_time,
        price=formatted_price,
        ticket_class=seat_class.replace('_', ' '),  # Hiển thị đẹp hơn
        total=formatted_total,
        available_seats=available_seats,
        flight=flight
    )



def add_customer():
    # Xử lý từng hành khách
    for p in range(int(request.form.get('passenger_count'))):  # Dùng hidden input để truyền số lượng
        name = request.form.get(f'passenger_name_{p}')
        birth_date = request.form.get(f'passenger_birth_{p}')
        gender = request.form.get(f'passenger_gender_{p}')
        seat_code = request.form.get(f'seat_{p}')  # Ghế mà khách hàng đã chọn

        # Kiểm tra seat_code có hợp lệ hay không
        if not seat_code:
            raise ValueError(f"Seat code is missing for passenger {p + 1}.")  # Thông báo nếu không có seat_code

        # Chuyển đổi ngày sinh về định dạng datetime
        birthday = datetime.strptime(birth_date, '%Y-%m-%d').date()

        # Tạo đối tượng Customer
        customer = Customer(
            name=name.split(" ", 1)[-1],  # Lấy tên
            last_name=name.split(" ", 1)[0],  # Lấy họ
            gender=Gender.Mr if gender == 'Male' else Gender.Ms,  # Map giá trị
            birthday=birthday
        )

        # Thêm vào session
        db.session.add(customer)
        db.session.commit()  # Lưu khách hàng vào DB

        # Tạo ticket cho khách hàng
        add_ticket(customer, seat_code)  # Gọi hàm add_ticket với seat_code


# Hàm thêm ticket cho khách hàng
def add_ticket(customer, seat_code):
    # Kiểm tra seat_code có hợp lệ hay không
    if not seat_code:
        raise ValueError("Seat code is missing.")  # Thông báo nếu không có seat_code

    # Lấy tất cả ghế có seat_code tương ứng
    seat = db.session.query(Seat).filter(Seat.seat_code == seat_code).first()
    if not seat:
        raise ValueError(f"Seat with code {seat_code} not found.")

    # Lấy flight_schedule_id từ SeatAssignment có seat_code tương ứng
    seat_assignment = db.session.query(SeatAssignment).join(Seat).filter(
        Seat.seat_code == seat_code,
        SeatAssignment.is_available == True
    ).first()

    if seat_assignment is None:
        raise ValueError(f"No available seat found for {seat_code}.")

    flight_schedule_id = seat_assignment.flight_schedule_id

    # Cập nhật SeatAssignment để đánh dấu ghế này đã được sử dụng
    seat_assignment.is_available = False
    db.session.commit()

    # Tạo ticket cho hành khách
    ticket = Ticket(
        seat_assignment_id=seat_assignment.id,
        user_id=current_user.id,  # Nếu người dùng đã đăng nhập
        customer_id=customer.id  # Liên kết ticket với customer
    )

    # Thêm ticket vào session và lưu vào DB
    db.session.add(ticket)
    db.session.commit()

def create_receipt(user_id, total, flight_route_id, ticket_count):
    # Tạo Receipt
    receipt = Receipt(
        user_id=user_id,
        total=total
    )
    db.session.add(receipt)
    db.session.commit()  # Lưu Receipt vào DB để lấy ID

    # Tạo ReceiptDetail với số lượng vé
    receipt_detail = ReceiptDetail(
        quantity=ticket_count,  # Số lượng vé được đặt
        unit_price=total // ticket_count if ticket_count > 0 else total,  # Giá mỗi vé
        receipt_id=receipt.id,
        flight_route_id=flight_route_id  # Liên kết với flight_route_id
    )
    db.session.add(receipt_detail)

    db.session.commit()  # Lưu ReceiptDetail vào DB
    return receipt



@app.route('/add_data', methods=['POST'])
def add_data():
    # Xử lý thông tin hành khách
    add_customer()

    # Lấy thông tin chuyến bay và tuyến bay
    flight_id = request.form.get('flight_id')  # Lấy ID chuyến bay
    flight = dao.get_flight_by_id(flight_id)  # Tìm chuyến bay trong DB
    if not flight:
        raise ValueError("Flight not found.")  # Xử lý nếu không tìm thấy chuyến bay

    flight_route_id = flight.flight_route_id  # Lấy flight_route_id từ chuyến bay

    # Lấy tổng tiền từ form và xử lý
    total_str = request.form.get('total')  # Giá trị từ form
    total = int(total_str.replace('.', '').replace(',', ''))  # Loại bỏ dấu phân cách và chuyển đổi

    user_id = current_user.id  # ID người dùng đã đăng nhập

    # Đếm số vé (hành khách)
    ticket_count = int(request.form.get('passenger_count'))

    # Tạo hóa đơn và chi tiết hóa đơn
    receipt = create_receipt(user_id, total, flight_route_id, ticket_count)

    # Lấy thông tin thời gian bay
    departure_date = request.form.get('departure_date')
    departure_time = request.form.get('departure_time')
    arrival_time = request.form.get('arrival_time')

    # Tạo danh sách hành khách để hiển thị trên hóa đơn
    passengers = []
    for p in range(ticket_count):
        name = request.form.get(f'passenger_name_{p}')
        seat_code = request.form.get(f'seat_{p}')
        passengers.append({'name': name, 'seat_code': seat_code})

    # Render hóa đơn
    return render_template('receipt.html', passengers=passengers,
                           flight=flight, departure_date=departure_date,
                           departure_time=departure_time, arrival_time=arrival_time,
                           total=total, receipt=receipt)



@app.route('/api/schedule', methods=['GET', 'POST'])
def flight_schedule():
    flightcodes = dao.load_flight()
    airports = dao.load_airport()

    if request.method == 'POST':
        data = request.get_json()

        # Tạo đối tượng lịch bay
        flight_schedule = FlightSchedule(
            dep_time=data['dep_time'],
            flight_time=data['flight_time'],
            flight_id=data['flight_id'],
            business_class_seat_size=data['business_class_seat_size'],
            economy_class_seat_size=data['economy_class_seat_size'],
            business_class_price=data['first_class_price'],
            economy_class_price=data['second_class_price']
        )
        db.session.add(flight_schedule)

        # Xử lý sân bay trung gian
        if data.get('ai_1'):
            intermediate_airport_1 = IntermediateAirport(
                airport_id=data['ai_1'],
                flight_id=data['flight_id'],
                stop_time=data['stop_time_1'],
                note=data['note_1']
            )
            db.session.add(intermediate_airport_1)

        if data.get('ai_2'):
            intermediate_airport_2 = IntermediateAirport(
                airport_id=data['ai_2'],
                flight_id=data['flight_id'],
                stop_time=data['stop_time_2'],
                note=data['note_2']
            )
            db.session.add(intermediate_airport_2)

        # Tạo đối tượng tuyến bay
        flight_route = FlightRoute(
            dep_airport_id=data['dep_airport'],
            des_airport_id=data['des_airport']
        )
        db.session.add(flight_route)

        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()

    return render_template('schedule.html', flightcodes=flightcodes, airports=airports)


if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
