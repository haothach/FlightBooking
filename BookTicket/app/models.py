from email.policy import default

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Date, DateTime
from sqlalchemy.orm import relationship, validates
from app import db, app
import hashlib
from enum import Enum as RoleEnum
from enum import Enum as AirlineEnum
import datetime

from flask_login import UserMixin

class BaseModel(db.Model):
    __abstract__=True
    id = Column(Integer, primary_key=True, autoincrement=True)
    #Các id ở dưới kế thừa từ basemodel


class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    STAFF = 3


class Airline(AirlineEnum):
    Bamboo_AirWays = 1
    Vietjet_Air = 2
    VietNam_Airline = 3


class User(BaseModel, UserMixin):

    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRole), default=UserRole.USER)


class Province(BaseModel):
    name = Column(String(100), nullable=False)

    airports = relationship('Airport', backref='province', lazy=True)

    def __str__(self):
        return self.name


class Airport(BaseModel):

    name = Column(String(100), nullable=False)
    add = Column(String(100), nullable=False)
    province_id = Column(Integer, ForeignKey(Province.id), nullable=False)

    dep_airports = relationship('FlightRoute', foreign_keys='FlightRoute.dep_airport_id', backref='dep_airport')
    des_airports = relationship('FlightRoute', foreign_keys='FlightRoute.des_airport_id', backref='des_airport')
    intermediate_airports = relationship('IntermediateAirport', backref='airport', lazy=True)

    def __str__(self):
        return self.name


class FlightRoute(BaseModel):

    dep_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)
    des_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)

    flights = relationship('Flight', backref='flight_route', lazy=True)
    inter_airports = relationship('IntermediateAirport', backref='flight_route', lazy=True)

    @validates('des_airport_id')
    def validate_airports(self, key, des_airport_id):
        if des_airport_id == self.dep_airport_id:
            raise ValueError("Departure and destination airports must be different.")
        return des_airport_id

    def __str__(self):
        dep_airport_name = self.dep_airport.name
        des_airport_name = self.des_airport.name
        return f"{dep_airport_name} -> {des_airport_name}"


class Airplane(BaseModel):

    name = Column(String(100), nullable=False)
    airplane_type = Column(Enum(Airline), nullable=False)
    capacity = Column(Integer, nullable=False)

    flights = relationship('Flight', backref='airplane', lazy=True)
    seats = relationship('Seat', backref='airplane', lazy=True)

    def __str__(self):
        return self.name


class Flight(BaseModel):

    dep_time = Column(DateTime, nullable=False)
    flight_time = Column(Integer, nullable=False)
    flight_code = Column(String(20), nullable=False)
    flight_route_id = Column(Integer, ForeignKey(FlightRoute.id), nullable=False)
    airplane_id = Column(Integer, ForeignKey(Airplane.id), nullable=False)

    flight_schedules = relationship('FlightSchedule', backref='flight', lazy=True)
    tickets = relationship('Ticket', backref='ticket', lazy=True)

    def __str__(self):
        return self.flight_code


class FlightSchedule(BaseModel):

    dep_time = Column(DateTime, nullable=False)
    first_class_seat_size = Column(Integer, nullable=False)
    first_class_ticket_price = Column(Integer, nullable=False)
    second_class_seat_size = Column(Integer, nullable=False)
    second_class_ticket_price = Column(Integer, nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False)


class IntermediateAirport(db.Model):
    airport_id = Column(Integer, ForeignKey(Airport.id), primary_key=True)
    flight_route_id = Column(Integer, ForeignKey(FlightRoute.id), primary_key=True)
    stop_time = Column(Integer, default=20)
    note = Column(String(100), nullable=True)


class TicketClass(BaseModel):

    name = Column(String(50), nullable=False)
    tickets = relationship('Ticket', backref='TicketClass', lazy=True)


class Ticket(BaseModel):

    date_created = Column(DateTime, default=datetime.datetime.utcnow)

    ticket_class_id = Column(Integer, ForeignKey(TicketClass.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False)

    order_details = relationship('OrderDetail', backref='ticket', lazy=True)
    seats = relationship('Seat', backref='ticket', lazy=True)


class Seat(BaseModel):

    seat_class = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=1)

    airplane_id = Column(Integer, ForeignKey(Airplane.id), nullable=False)
    ticket_id = Column(Integer, ForeignKey(Ticket.id), nullable=False)


class Bill(BaseModel):

    issueDate = Column(DateTime, nullable=False)
    total = Column(Float, nullable=False)
    is_Paid = Column(Boolean, default=False)
    note = Column(String(100), nullable=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)

    orders = relationship('Order', backref='bill', lazy=True)


class Order(BaseModel):

    order_day = Column(DateTime, nullable=False)
    order_method = Column(Integer, default=1)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)

    bill_id = Column(Integer, ForeignKey(Bill.id), nullable=False)

    order_details = relationship('OrderDetail', backref='order', lazy=True)


class OrderDetail(BaseModel):

    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=True)
    total = Column(Float, nullable=True)

    ticket_id = Column(Integer, ForeignKey(Ticket.id), nullable=False)
    order_id = Column(Integer, ForeignKey(Order.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # u = User(name="admin", username="admin", password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
        #          avatar="https://res.cloudinary.com/dnoubiojc/image/upload/v1731852091/cld-sample-5.jpg",
        #          user_role=UserRole.ADMIN)
        # db.session.add(u)
        #
        # provinces = [{
        #     "name": "TP HCM"
        # }, {
        #     "name": "Hà Nội"
        # }, {
        #     "name": "Đà Nẵng"
        # }, {
        #     "name": "Nghệ An"
        # }, {
        #     "name": "Cần Thơ"
        # }, {
        #     "name": "Hải Phòng"
        # }, {
        #     "name": "Đà Lạt"
        # }, {
        #     "name": "Quảng Ninh"
        # }, {
        #     "name": "Khánh Hòa"
        # }, {
        #     "name": "Bình Dương"
        # }]
        #
        # for p in provinces:
        #     p = Province(**p)
        #     db.session.add(p)
        #
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
        # ]
        #
        # for a in airports:
        #     a = Airport(**a)
        #     db.session.add(a)
        #
        # # # Add airplanes
        # airplanes = [
        #     {"name": "MH390", "airplane_type": Airline.Bamboo_AirWays, "capacity": 200},
        #     {"name": "MH800", "airplane_type": Airline.Vietjet_Air, "capacity": 180},
        #     {"name": "MH060", "airplane_type": Airline.VietNam_Airline, "capacity": 220},
        # ]
        #
        # for a in airplanes:
        #     airplane = Airplane(**a)
        #     db.session.add(airplane)
        #
        # flight_routes = [
        #     {"dep_airport_id": 1, "des_airport_id": 2},  # Tân Sơn Nhất -> Nội Bài
        #     {"dep_airport_id": 2, "des_airport_id": 3},  # Nội Bài -> Đà Nẵng
        #     {"dep_airport_id": 3, "des_airport_id": 4},  # Đà Nẵng -> Vinh
        # ]
        #
        # for route in flight_routes:
        #     flight_route = FlightRoute(**route)
        #     db.session.add(flight_route)
        #
        # # Add flights
        # flights = [
        #     {"dep_time": datetime.datetime(2024, 12, 1, 9, 0), "flight_time": 120, "flight_code": "VN123",
        #      "flight_route_id": 1, "airplane_id": 1},
        #     {"dep_time": datetime.datetime(2024, 12, 1, 14, 30), "flight_time": 90, "flight_code": "VN456",
        #      "flight_route_id": 2, "airplane_id": 2},
        #     {"dep_time": datetime.datetime(2024, 12, 1, 17, 15), "flight_time": 150, "flight_code": "VN789",
        #      "flight_route_id": 3, "airplane_id": 3},
        # ]
        # for f in flights:
        #     f = Flight(**f)
        #     db.session.add(f)
        # db.session.commit()
        #
        #
        # # Add flight schedules
        # flight_schedules = [
        #     {"dep_time": datetime.datetime(2024, 12, 1, 9, 0), "first_class_seat_size": 20,
        #      "first_class_ticket_price": 500000, "second_class_seat_size": 100, "second_class_ticket_price": 200000,
        #      "flight_id": 1},
        #     {"dep_time": datetime.datetime(2024, 12, 1, 14, 30), "first_class_seat_size": 15,
        #      "first_class_ticket_price": 450000, "second_class_seat_size": 80, "second_class_ticket_price": 180000,
        #      "flight_id": 2},
        #     {"dep_time": datetime.datetime(2024, 12, 1, 17, 15), "first_class_seat_size": 10,
        #      "first_class_ticket_price": 550000, "second_class_seat_size": 120, "second_class_ticket_price": 220000,
        #      "flight_id": 3},
        # ]
        # for fs in flight_schedules:
        #     fs = FlightSchedule(**fs)
        #     db.session.add(fs)
        # db.session.commit()
        #
        # #
        # # # Add intermediate airports
        # intermediate_airports = [
        #     {"airport_id": 2, "flight_route_id": 1, "stop_time": 30, "note": "Refueling stop"},
        #     {"airport_id": 3, "flight_route_id": 2, "stop_time": 25, "note": "Passenger exchange"},
        #     {"airport_id": 4, "flight_route_id": 3, "stop_time": 20, "note": "Technical stop"},
        # ]
        # for ia in intermediate_airports:
        #     ia = IntermediateAirport(**ia)
        #     db.session.add(ia)
        #
        #
        # # Add ticket classes
        # ticket_classes = [
        #     {"name": "First Class"},
        #     {"name": "Second Class"},
        # ]
        # for tc in ticket_classes:
        #     tc = TicketClass(**tc)
        #     db.session.add(tc)
        #
        # # Add tickets
        # tickets = [
        #     {"ticket_class_id": 1, "flight_id": 1},
        #     {"ticket_class_id": 2, "flight_id": 1},
        #     {"ticket_class_id": 1, "flight_id": 2},
        #     {"ticket_class_id": 2, "flight_id": 2},
        # ]
        # for t in tickets:
        #     t = Ticket(**t)
        #     db.session.add(t)
        #
        # # Add seats
        # seats = [
        #     {"seat_class": 1, "is_available": True, "airplane_id": 1, "ticket_id": 1},
        #     {"seat_class": 2, "is_available": True, "airplane_id": 1, "ticket_id": 2},
        #     {"seat_class": 1, "is_available": True, "airplane_id": 2, "ticket_id": 3},
        #     {"seat_class": 2, "is_available": True, "airplane_id": 2, "ticket_id": 4},
        # ]
        # for s in seats:
        #     s = Seat(**s)
        #     db.session.add(s)
        #
        # # Add bills
        # bills = [
        #     {"issueDate": datetime.datetime(2024, 11, 30), "total": 600, "is_Paid": True,
        #      "note": "Paid via credit card"},
        #     {"issueDate": datetime.datetime(2024, 11, 29), "total": 400, "is_Paid": False,
        #      "note": "Pending payment"},
        # ]
        # for b in bills:
        #     b = Bill(**b)
        #     db.session.add(b)
        #
        # # Add orders
        # orders = [
        #     {"order_day": datetime.datetime(2024, 11, 28), "order_method": 1, "bill_id": 1},
        #     {"order_day": datetime.datetime(2024, 11, 27), "order_method": 2, "bill_id": 2},
        # ]
        # for o in orders:
        #     o = Order(**o)
        #     db.session.add(o)
        #
        # # Add order details
        # order_details = [
        #     {"quantity": 2, "unit_price": 150, "total": 300, "ticket_id": 1, "order_id": 1},
        #     {"quantity": 1, "unit_price": 100, "total": 100, "ticket_id": 2, "order_id": 1},
        #     {"quantity": 1, "unit_price": 200, "total": 200, "ticket_id": 3, "order_id": 2},
        # ]
        #
        #
        # for od in order_details:
        #     od = OrderDetail(**od)
        #     db.session.add(od)
        #
        # db.session.commit()
