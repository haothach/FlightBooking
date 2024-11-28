import math
import sqlite3

import sqlalchemy
from flask import render_template, request, redirect
import dao
from app import app, login
from flask_login import login_user, logout_user
from datetime import datetime


# @app.route("/")
# def index():
#     return render_template("index.html")

@app.route("/")
def index():
    provinces = dao.load_province()
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    return render_template('index.html', provinces=provinces,
                           destination=destination, departure=departure)


@app.route("/search")
def search():
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure-date')
    passenger = request.args.get('passengers')

    flights = dao.query_database(departure, destination, departure_date)

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


@app.route("/login", methods=['get', 'post'])
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect('/')

    return render_template('login.html')


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    app.run(debug=True)
