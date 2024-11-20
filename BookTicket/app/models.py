from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship, validates
from app import db, app
import hashlib
from enum import Enum as RoleEnum
from enum import Enum as FlightTypeEnum
from flask_login import UserMixin


class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    STAFF = 3

class FlightType(FlightTypeEnum):
    Bamboo_AirWays = 1
    Vietjet_Air = 2
    VietNam_Airline = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRole), default=UserRole.USER)


class Province(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    airports = relationship('Airport', backref='province', lazy=True)

    def __str__(self):
        return self.name


class Airport(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    add = Column(String(100), nullable=False)
    province_id = Column(Integer, ForeignKey(Province.id), nullable=False)

    dep_airports = relationship('FlightRoute', foreign_keys='FlightRoute.dep_airport_id', backref='dep_airport')
    des_airports = relationship('FlightRoute', foreign_keys='FlightRoute.des_airport_id', backref='des_airport')
    inter_airports = relationship('IntermediateAirport', backref="airport", lazy=True)


class IntermediateAirport(Airport):
    id = Column(Integer, ForeignKey(Airport.id), primary_key=True, autoincrement=True)
    stop_time = Column(Integer, nullable=False)
    note = Column(String(100), nullable=True)


class FlightSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    dep_date = Column(Date, nullable=False)
    arr_date = Column(Date, nullable=False)
    num_seat = Column(Integer, nullable=False)
    num_seat_first = Column(Integer, nullable=False)
    num_seat_second = Column(Integer, nullable=False)


class Flight(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_type = Column(Enum(FlightType))

class Airplane(db.Model):


class FlightRoute(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)

    dep_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)
    des_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)

    @validates('des_airport_id')
    def validate_airports(self, key, des_airport_id):
        if des_airport_id == self.dep_airport_id:
            raise ValueError("Departure and destination airports must be different.")
        return des_airport_id


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()

        # u = User(name="admin", username="admin", password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
        #          avatar="https://res.cloudinary.com/dnoubiojc/image/upload/v1731852091/cld-sample-5.jpg",
        #          user_role=UserRole.ADMIN)
        # db.session.add(u)
        #
        # provinces = [{
        #     "name": "TP HCM"
        # },{
        #     "name": "Hà Nội"
        # },{
        #     "name": "Đà Nẵng"
        # },{
        #     "name": "Nghệ An"
        # },{
        #     "name": "Cần Thơ"
        # },{
        #     "name": "Hải Phòng"
        # },{
        #     "name": "Đà Lạt"
        # },{
        #     "name": "Quảng Ninh"
        # },{
        #     "name": "Khánh Hòa"
        # },{
        #     "name": "Bình Dương"
        # },{
        #     "name": "Hải Dương"
        # },{
        #     "name": "Phú Yên"
        # },{
        #     "name": "Thanh Hóa"
        # }]
        #
        # for p in provinces:
        #     p = Province(**p)
        #     db.session.add(p)

        # airports = [
        #     {"name": "Tân Sơn Nhất", "add": "Phường 2, 4 và 15, Quận Tân Bình", "province_id": 1},
        #     {"name": "Nội Bài", "add": "Số 200 đường Phạm Văn Đồng, Hà Nội", "province_id": 2},
        #     {"name": "Đà Nẵng", "add": "Số 02 đường Duy Tân, Quận Hải Châu, Đà Nẵng", "province_id": 3},
        #     {"name": "Vinh", "add": "Số 1 đường Nguyễn Sỹ Sách, TP Vinh, Nghệ An", "province_id": 4},
        #     {"name": "Cần Thơ", "add": "Số 60 đường Mậu Thân, Cần Thơ", "province_id": 5},
        #     {"name": "Cát Bì", "add": "Số 15 đường Nguyễn Đức Cảnh, Hải Phòng", "province_id": 6},
        #     {"name": "Liên Khương", "add": "Xã Liên Nghĩa, Huyện Đức Trọng, Lâm Đồng", "province_id": 7},
        #     {"name": "Vân Đồn", "add": "Số 28 đường Vân Đồn, Quảng Ninh", "province_id": 8},
        #     {"name": "Cam Ranh", "add": "Đường Nguyễn Tất Thành, thành phố Cam Ranh, tỉnh Khánh Hòa", "province_id": 9},
        #     {"name": "Long Thành", "add": "Xã Long Thanh, Huyện Long Thành, tỉnh Đồng Nai", "province_id": 10},
        #     {"name": "Hải Dương", "add": "Xã Hưng Đạo, TP Hải Dương", "province_id": 11},
        #     {"name": "Phú Yên", "add": "Phú Yên Airport, Tuy Hòa, Phú Yên", "province_id": 12},
        #     {"name": "Thác Bà", "add": "Xã Lâm Thao, Thanh Hóa", "province_id": 13}
        # ]
        #
        # for a in airports:
        #     a = Airport(**a)
        #     db.session.add(a)
        #
        # f = FlightRoute(dep_airport_id=1, des_airport_id=2)
        # db.session.add(f)

        # i = IntermediateAirport()

        db.session.commit()
