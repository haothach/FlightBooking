from app.models import User, Province, Airport, Flight, FlightRoute
from app import app, db
import hashlib
import cloudinary.uploader


def load_province():
    return Province.query.order_by('id').all()


def load_flight_route():
    return Flight.query.order_by('id').all()


def load_flight_route():
    return FlightRoute.query.order_by('id').all()


def load_flight(departure=None, destination=None):
    return Flight.query.order_by('id').all()


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User(name=name, username=username, password=password,
             avatar="https://res.cloudinary.com/dxxwcby8l/image/upload/v1691062682/tkeflqgroeil781yplxt.jpg")

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        print(res)
        u.avatar = res.get("secure_url")

    db.session.add(u)
    db.session.commit()


def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password)).first()


def get_user_by_id(id):
    return User.query.get(id)
