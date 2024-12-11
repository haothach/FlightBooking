import hashlib
import string

from flask import render_template, request, redirect
import dao
from app import app, login
from flask_login import login_user, logout_user
from app.models import UserRole


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
    departure_date = request.args.get('departure-date')
    passenger = request.args.get('passengers')
    time_range = request.args.get('time_range')
    arrival_time_range = request.args.get('arrival_time_range')
    # Lấy danh sách chuyến bay
    flights = dao.load_flights(departure, destination, departure_date)

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
    return render_template('search.html', departure=departure, destination=destination,
                           departure_date=departure_date, passenger=passenger, flights=flights)


@app.route("/register", methods=['get', 'post'])
def register_view():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not password.__eq__(confirm):
            err_msg = 'Mật khẩu không khớp!'
        else:
            data = request.form.copy()
            del data['confirm']
            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)

            return redirect('/login')

    return render_template('register.html', err_msg=err_msg)


@app.route("/login", methods=['post', 'get'])
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
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


if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
