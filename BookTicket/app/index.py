import math

from flask import render_template, request, redirect
import dao
from app import app, login
from flask_login import login_user, logout_user


# @app.route("/")
# def index():
#     return render_template("index.html")

@app.route("/")
def index():
    provinces = dao.load_province()
    # trip_type = request.args.get('tripType')
    # departure = request.args.get('departure')
    # destination = request.args.get('destination')
    # dep_date = request.args.get('departureDate')
    #
    # if not trip_type.__eq__('oneWay'):
    #     re_date = request.args.get('returnDate')
    #     return render_template('index.html', provinces=provinces, tripType=trip_type, depature=departure,
    #                        destination=destination, departureDate=dep_date, returnDate=re_date)
    #
    #
    # return render_template('index.html',  provinces=provinces, tripType=trip_type, depature=departure,
    #                        destination=destination, departureDate=dep_date)

    return render_template('index.html', pros=provinces)


@app.route("/searchflights")
def searchflights():
    return render_template('searchflights.html')


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
