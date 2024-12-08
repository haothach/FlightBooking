from email.policy import default

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Date, DateTime
from sqlalchemy.orm import relationship, validates
from app import db, app
import hashlib
from enum import Enum as RoleEnum
from enum import Enum as AirlineEnum
from enum import Enum as TicketClassEnum
import datetime
from flask_login import UserMixin


class BaseModel(db.Model):

    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Các id ở dưới kế thừa từ basemodel


class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    STAFF = 3


class Airline(AirlineEnum):
    Bamboo_AirWays = 1
    Vietjet_Air = 2
    VietNam_Airline = 3


class TicketClass(TicketClassEnum):
    Business_Class = 1
    Economy_Class = 2


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

    @validates('dep_airport_id', 'des_airport_id')
    def validate_airports_and_duplicates(self, key, value):
        # Nếu kiểm tra 'des_airport_id', đảm bảo sân bay đi và đến không trùng nhau
        if key == 'des_airport_id' and value == self.dep_airport_id:
            raise ValueError("Departure and destination airports must be different.")
        # Kiểm tra trùng lặp tuyến bay
        existing_route = FlightRoute.query.filter_by(
            dep_airport_id=self.dep_airport_id if key != 'dep_airport_id' else value,
            des_airport_id=self.des_airport_id if key != 'des_airport_id' else value
        ).first()
        if existing_route and existing_route.id != self.id:
            raise ValueError("This flight route already exists.")
        return value

    def __str__(self):
        dep_airport_name = self.dep_airport.name
        des_airport_name = self.des_airport.name
        dep_province_name = self.dep_airport.province.name
        des_province_name = self.des_airport.province.name
        return f"{dep_province_name} ({dep_airport_name}) -> {des_province_name} ({des_airport_name})"


class Airplane(BaseModel):

    name = Column(String(100), nullable=False)
    airplane_type = Column(Enum(Airline), nullable=False)
    capacity = Column(Integer, nullable=False)
    first_class_seat_size = Column(Integer, nullable=False)
    second_class_seat_size = Column(Integer, nullable=False)

    flights = relationship('Flight', backref='airplane', lazy=True)
    seats = relationship('Seat', backref='airplane', lazy=True)

    def __str__(self):
        return self.name


class Flight(BaseModel):

    flight_code = Column(String(20), nullable=False)
    flight_route_id = Column(Integer, ForeignKey(FlightRoute.id), nullable=False)
    airplane_id = Column(Integer, ForeignKey(Airplane.id), nullable=False)

    flight_schedules = relationship('FlightSchedule', backref='flight', lazy=True)
    tickets = relationship('Ticket', backref='flight', lazy=True)
    inter_airports = relationship('IntermediateAirport', backref='flight', lazy=True)

    def __str__(self):
        return self.flight_code


class FlightSchedule(BaseModel):

    dep_time = Column(DateTime, nullable=False)
    flight_time = Column(Integer, nullable=False)
    first_class_ticket_price = Column(Integer, nullable=False)
    second_class_ticket_price = Column(Integer, nullable=False)

    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False)


class IntermediateAirport(db.Model):
    airport_id = Column(Integer, ForeignKey(Airport.id), primary_key=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), primary_key=True)
    stop_time = Column(Integer, default=20)
    note = Column(String(100), nullable=True)

    def __str__(self):
        return self.airport.name


class Ticket(BaseModel):

    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    ticket_class = Column(Enum(TicketClass), nullable=False)

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


class Policy(BaseModel):
    numberAirport = Column(Integer, nullable=False)
    minimumFlightTime = Column(Integer, nullable=False)
    maxIntermediateAirports = Column(Integer, nullable=False)
    minStopTime = Column(Integer, nullable=False)
    maxStopTime = Column(Integer, nullable=False)
    numTicketClasses = Column(Integer, nullable=False)
    ticketPrice = Column(Integer, nullable=False)
    ticketSaleTime = Column(Integer, nullable=False)
    ticketBookingTime = Column(Integer, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        u = User(name="admin", username="admin", password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                 avatar="https://res.cloudinary.com/dnoubiojc/image/upload/v1731852091/cld-sample-5.jpg",
                 user_role=UserRole.ADMIN)
        db.session.add(u)
        db.session.commit()
        provinces = [{
            "name": "TP HCM"
        }, {
            "name": "Hà Nội"
        }, {
            "name": "Đà Nẵng"
        }, {
            "name": "Nghệ An"
        }, {
            "name": "Cần Thơ"
        }, {
            "name": "Hải Phòng"
        }, {
            "name": "Đà Lạt"
        }, {
            "name": "Quảng Ninh"
        }, {
            "name": "Khánh Hòa"
        }, {
            "name": "Bình Dương"
        }]

        for p in provinces:
            p = Province(**p)
            db.session.add(p)
        db.session.commit()
        airports = [
            {"name": "Tân Sơn Nhất", "add": "Phường 2, 4 và 15, Quận Tân Bình", "province_id": 1},
            {"name": "Nội Bài", "add": "Số 200 đường Phạm Văn Đồng, Hà Nội", "province_id": 2},
            {"name": "Đà Nẵng", "add": "Số 02 đường Duy Tân, Quận Hải Châu, Đà Nẵng", "province_id": 3},
            {"name": "Vinh", "add": "Số 1 đường Nguyễn Sỹ Sách, TP Vinh, Nghệ An", "province_id": 4},
            {"name": "Cần Thơ", "add": "Số 60 đường Mậu Thân, Cần Thơ", "province_id": 5},
            {"name": "Cát Bì", "add": "Số 15 đường Nguyễn Đức Cảnh, Hải Phòng", "province_id": 6},
            {"name": "Liên Khương", "add": "Xã Liên Nghĩa, Huyện Đức Trọng, Lâm Đồng", "province_id": 7},
            {"name": "Vân Đồn", "add": "Số 28 đường Vân Đồn, Quảng Ninh", "province_id": 8},
            {"name": "Long Thành", "add": "Xã Long Thanh, Huyện Long Thành, tỉnh Đồng Nai", "province_id": 9},
        ]

        for a in airports:
            a = Airport(**a)
            db.session.add(a)
        db.session.commit()
        # Add airplanes
        airplanes = [
            {"name": "AIRBUS A350", "airplane_type": Airline.VietNam_Airline, "capacity": 305,
                "first_class_seat_size": 29, "second_class_seat_size": 276},
            {"name": "AIRBUS A302", "airplane_type": Airline.VietNam_Airline, "capacity": 184,
             "first_class_seat_size": 16, "second_class_seat_size": 162},
            {"name": "BOEING 787", "airplane_type": Airline.VietNam_Airline, "capacity": 274,
             "first_class_seat_size": 28, "second_class_seat_size": 246},
        ]

        for a in airplanes:
            airplane = Airplane(**a)
            db.session.add(airplane)

        flight_routes = [
            {"dep_airport_id": 1, "des_airport_id": 2},  # Tân Sơn Nhất -> Nội Bài
            {"dep_airport_id": 2, "des_airport_id": 3},  # Nội Bài -> Đà Nẵng
            {"dep_airport_id": 3, "des_airport_id": 4},  # Đà Nẵng -> Vinh
            {"dep_airport_id": 1, "des_airport_id": 5},  # Tân Sơn Nhất -> Cần Thơ
        ]

        for route in flight_routes:
            flight_route = FlightRoute(**route)
            db.session.add(flight_route)

        # Thêm dữ liệu vào bảng Flight
        flights = [
            {"flight_code": "VN 216", "flight_route_id": 1, "airplane_id": 1},
            {"flight_code": "VN 157", "flight_route_id": 2, "airplane_id": 2},
            {"flight_code": "VN789", "flight_route_id": 3, "airplane_id": 3},
        ]

        for flight in flights:
            flight_obj = Flight(**flight)
            db.session.add(flight_obj)

        # Thêm dữ liệu vào bảng FlightSchedule

        flight_schedules = [
            {
                "dep_time": datetime.datetime(2024, 12, 3, 8, 0),
                "flight_time": 120,
                "first_class_ticket_price": 2000000,
                "second_class_ticket_price": 1000000,
                "flight_id": 1,
            },
            {
                "dep_time": datetime.datetime(2024, 12, 20, 16, 50),
                "flight_time": 1065,
                "first_class_ticket_price": 1800000,
                "second_class_ticket_price": 800000,
                "flight_id": 3,
            },
        ]

        for schedule in flight_schedules:
            flight_schedule = FlightSchedule(**schedule)
            db.session.add(flight_schedule)

        # Thêm dữ liệu vào bảng IntermediateAirport
        intermediate_airports = [
            {"airport_id": 2, "flight_id": 3, "stop_time": 160, "note": "Transit in Ha Noi"},
        ]

        for intermediate in intermediate_airports:
            inter_airport = IntermediateAirport(**intermediate)
            db.session.add(inter_airport)

        # Thêm dữ liệu vào bảng Ticket
        tickets = [
            {"flight_id": 1, "ticket_class": TicketClass.Economy_Class},
            {"flight_id": 1, "ticket_class": TicketClass.Business_Class},
            {"flight_id": 2, "ticket_class": TicketClass.Economy_Class},
            {"flight_id": 2, "ticket_class": TicketClass.Business_Class},
            {"flight_id": 3, "ticket_class": TicketClass.Economy_Class},
            {"flight_id": 3, "ticket_class": TicketClass.Business_Class},
        ]

        for ticket in tickets:
            ticket_obj = Ticket(**ticket)
            db.session.add(ticket_obj)


        # Thêm dữ liệu vào bảng Bill
        bills = [
            {"issueDate": datetime.datetime(2024, 12, 3), "total": 3000000, "is_Paid": True},
        ]

        for bill in bills:
            bill_obj = Bill(**bill)
            db.session.add(bill_obj)



        # Thêm dữ liệu vào bảng Order
        orders = [
            {"order_day": datetime.datetime(2024, 12, 3), "bill_id": 1},
        ]

        for order in orders:
            order_obj = Order(**order)
            db.session.add(order_obj)



        # Thêm dữ liệu vào bảng OrderDetail
        order_details = [
            {"quantity": 2, "unit_price": 1000000, "total": 2000000, "ticket_id": 1, "order_id": 1},
        ]

        for detail in order_details:
            order_detail = OrderDetail(**detail)
            db.session.add(order_detail)



        #Thêm dữ liệu vào bảng Seat
        seats = [
            {"seat_class": 1, "is_available": True, "airplane_id": 1, "ticket_id": 1},  # Ghế phổ thông
            {"seat_class": 2, "is_available": False, "airplane_id": 1, "ticket_id": 1},  # Ghế thương gia
            {"seat_class": 1, "is_available": True, "airplane_id": 2, "ticket_id": 2},  # Ghế phổ thông
            {"seat_class": 2, "is_available": True, "airplane_id": 2, "ticket_id": 3},  # Ghế thương gia
        ]
        for seat in seats:
            seat_obj = Seat(**seat)
            db.session.add(seat_obj)

        new_policy = Policy(
            numberAirport=10,  # Số lượng sân bay tối đa
            minimumFlightTime=30,  # Thời gian bay tối thiểu 30 phút
            maxIntermediateAirports=2,  # Số sân bay trung gian tối đa
            minStopTime=20,  # Thời gian dừng tối thiểu tại sân bay trung gian
            maxStopTime=30,  # Thời gian dừng tối đa tại sân bay trung gian
            numTicketClasses=2,  # Số hạng vé (2 hạng vé)
            ticketPrice=1000,  # Giá vé (ví dụ: 1000 là đơn vị tiền tệ)
            ticketSaleTime=1440,  # Thời gian bán vé (ví dụ: 1440 phút = 1 ngày)
            ticketBookingTime=240,  # Thời gian đặt vé (ví dụ: 240 phút = 4 giờ trước khi chuyến bay)
        )
        # Thêm vào session và commit
        db.session.add(new_policy)
        db.session.commit()