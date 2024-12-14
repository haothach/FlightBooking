from email.policy import default

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Date, DateTime, event
from sqlalchemy.orm import relationship, validates, backref
from app import db, app
import hashlib
from enum import Enum as RoleEnum
from enum import Enum as AirlineEnum
from enum import Enum as TicketClassEnum
import datetime
from flask_login import UserMixin
import math


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

    orders = relationship('Order', backref='user', lazy=True)


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
    business_class_seat_size = Column(Integer, nullable=False)
    economic_class_seat_size = Column(Integer, nullable=False)

    flights = relationship('Flight', backref='airplane', lazy=True)
    seats = relationship('Seat', backref='airplane', lazy=True)

    def __str__(self):
        return self.name

    def generate_seats(self):
        """Tạo danh sách ghế dựa trên số lượng ghế business và economy."""
        seats = []

        seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']  # Các cột từ A đến F

        # Tạo ghế Business
        for row in range(1, math.ceil(self.business_class_seat_size / 6) + 1):
            for col_idx, letter in enumerate(seat_letters):
                if len(seats) >= self.business_class_seat_size:  # Dừng nếu đủ số ghế
                    break
                seat_code = f"B{row}{letter}"
                seats.append(Seat(
                    seat_code=seat_code,
                    seat_class=TicketClass.Business_Class,
                    airplane_id=self.id
                ))

        # Tạo ghế Economy
        for row in range(1, math.ceil(self.economic_class_seat_size / 6) + 1):
            for col_idx, letter in enumerate(seat_letters):
                if len(seats) - self.business_class_seat_size >= self.economic_class_seat_size:
                    break
                seat_code = f"E{row}{letter}"
                seats.append(Seat(
                    seat_code=seat_code,
                    seat_class=TicketClass.Economy_Class,
                    airplane_id=self.id
                ))

        # Thêm danh sách ghế vào database
        db.session.add_all(seats)
        db.session.commit()


class Flight(BaseModel):
    flight_code = Column(String(20), nullable=False, unique=True)
    flight_route_id = Column(Integer, ForeignKey(FlightRoute.id), nullable=False)
    airplane_id = Column(Integer, ForeignKey(Airplane.id), nullable=False)

    # flight_schedules = relationship('FlightSchedule', backref='flight', lazy=True)
    inter_airports = relationship('IntermediateAirport', backref='flight', lazy=True)
    flight_schedules = relationship('FlightSchedule', backref='flight', lazy=True)

    def __str__(self):
        return self.flight_code


class FlightSchedule(BaseModel):
    dep_time = Column(DateTime, nullable=False)
    flight_time = Column(Integer, nullable=False)
    business_class_seat_size = Column(Integer, nullable=False)
    economic_class_seat_size = Column(Integer, nullable=False)
    business_class_price = Column(Integer, nullable=False)
    economic_class_price = Column(Integer, nullable=False)

    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, unique=True)

    seat_assignments = relationship('SeatAssignment', backref='flight_schedule', lazy=True)
    tickets = relationship('Ticket', backref='flight', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        flight_id = kwargs.get('flight_id')
        if flight_id is None:
            raise ValueError("Flight ID must be provided.")

        # Lấy thông tin chuyến bay từ flight_id
        flight = db.session.get(Flight, flight_id)
        if flight is None:
            raise ValueError(f"No flight found with ID {flight_id}.")  # Xử lý nếu không tìm thấy chuyến bay

        # Kiểm tra nếu chuyến bay không có máy bay (airplane)
        airplane = flight.airplane
        if airplane is None:
            raise ValueError("The flight must be associated with an airplane.")  # Xử lý nếu chuyến bay không có máy bay

        # Kiểm tra số lượng ghế hạng business và economic không vượt quá khả năng của máy bay
        if self.business_class_seat_size > airplane.business_class_seat_size:
            raise ValueError(
                f"Business class seat size cannot exceed the airplane's business capacity ({airplane.business_class_seat_size})."
            )

        if self.economic_class_seat_size > airplane.economic_class_seat_size:
            raise ValueError(
                f"Economic class seat size cannot exceed the airplane's economic capacity ({airplane.economic_class_seat_size})."
            )

    def create_seat_assignments(self):
        """
        Tạo danh sách SeatAssignment cho lịch bay dựa trên số ghế được định sẵn.
        """
        # Lấy đối tượng Flight từ flight_id
        flight = db.session.query(Flight).filter_by(id=self.flight_id).first()

        # Kiểm tra nếu không tìm thấy Flight, thoát ra
        if not flight:
            print(f"Flight with id {self.flight_id} not found.")
            return

        # Lấy danh sách ghế business và economy với số lượng giới hạn theo yêu cầu
        business_seats = db.session.query(Seat).filter(
            Seat.airplane_id == flight.airplane_id,
            Seat.seat_class == TicketClass.Business_Class
        ).limit(self.business_class_seat_size).all()

        economic_seats = db.session.query(Seat).filter(
            Seat.airplane_id == flight.airplane_id,
            Seat.seat_class == TicketClass.Economy_Class
        ).limit(self.economic_class_seat_size).all()

        # Tạo SeatAssignment cho các ghế business
        for seat in business_seats:
            seat_assignment = SeatAssignment(seat_id=seat.id, flight_schedule_id=self.id, is_available=True)
            db.session.add(seat_assignment)

        # Tạo SeatAssignment cho các ghế economic
        for seat in economic_seats:
            seat_assignment = SeatAssignment(seat_id=seat.id, flight_schedule_id=self.id, is_available=True)
            db.session.add(seat_assignment)

        # Commit vào cơ sở dữ liệu
        db.session.commit()


class Seat(BaseModel):
    seat_code = Column(String(10), nullable=False)
    seat_class = Column(Enum(TicketClass), nullable=False)

    airplane_id = Column(Integer, ForeignKey(Airplane.id), nullable=False)

    tickets = relationship('Ticket', backref='seat', lazy=True)
    seat_assignments = relationship('SeatAssignment', backref='seat', lazy=True)

    def __str__(self):
        return f"{self.seat_code} ({self.seat_class.name})"


class SeatAssignment(BaseModel):
    seat_id = Column(Integer, ForeignKey(Seat.id), primary_key=True)
    flight_schedule_id = Column(Integer, ForeignKey(FlightSchedule.id), primary_key=True)
    is_available = Column(Boolean, default=1)


class IntermediateAirport(db.Model):
    airport_id = Column(Integer, ForeignKey(Airport.id), primary_key=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), primary_key=True)
    stop_time = Column(Integer, default=20)
    note = Column(String(100), nullable=True)

    def __str__(self):
        return self.airport.name


class Ticket(BaseModel):
    date_created = Column(DateTime, default=datetime.datetime.utcnow)

    seat_id = Column(Integer, ForeignKey(Seat.id), nullable=False)
    flight_schedule_id = Column(Integer, ForeignKey(FlightSchedule.id), nullable=False)

    order_details = relationship('OrderDetail', backref='ticket', lazy=True)


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

    cus_id = Column(Integer, ForeignKey(User.id), nullable=False)
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

        # Chuyển đổi dữ liệu từ danh sách airplanes thành các đối tượng Airplane
        airplanes = [
            {
                "name": "Airbus A320",
                "airplane_type": Airline.VietNam_Airline,
                "business_class_seat_size": 5 * 4,  # 5 hàng * 4 ghế/hàng
                "economic_class_seat_size": 10 * 6,  # 20 hàng * 6 ghế/hàng
            },
            {
                "name": "Boeing 787",
                "airplane_type": Airline.Bamboo_AirWays,
                "business_class_seat_size": 5 * 5,
                "economic_class_seat_size": 10 * 7,
            },
            {
                "name": "Airbus A321",
                "airplane_type": Airline.Vietjet_Air,
                "business_class_seat_size": 6 * 4,
                "economic_class_seat_size": 14 * 6,
            },
            {
                "name": "Boeing 737",
                "airplane_type": Airline.VietNam_Airline,
                "business_class_seat_size": 4 * 4,
                "economic_class_seat_size": 10 * 6,
            },
            {
                "name": "Airbus A380",
                "airplane_type": Airline.Bamboo_AirWays,
                "business_class_seat_size": 5 * 6,
                "economic_class_seat_size": 8 * 8,
            },
            {
                "name": "Boeing 777",
                "airplane_type": Airline.VietNam_Airline,
                "business_class_seat_size": 5 * 5,
                "economic_class_seat_size": 7 * 7,
            },
            {
                "name": "Embraer E195",
                "airplane_type": Airline.Vietjet_Air,
                "business_class_seat_size": 5 * 4,
                "economic_class_seat_size": 8 * 6,
            }
        ]

        for ap in airplanes:
            # Tạo đối tượng Airplane
            airplane = Airplane(**ap)

            # Thêm vào session và commit để lấy `id`
            db.session.add(airplane)
            db.session.commit()

            # Gọi hàm generate_seats sau khi `id` đã được gán
            airplane.generate_seats()

        flight_routes = [
            {"dep_airport_id": 1, "des_airport_id": 2},  # Tuyến bay từ Tân Sơn Nhất đến Nội Bài
            {"dep_airport_id": 2, "des_airport_id": 3},  # Tuyến bay từ Nội Bài đến Đà Nẵng
            {"dep_airport_id": 3, "des_airport_id": 4},  # Tuyến bay từ Đà Nẵng đến Vinh
            {"dep_airport_id": 4, "des_airport_id": 5},  # Tuyến bay từ Vinh đến Cần Thơ
            {"dep_airport_id": 1, "des_airport_id": 6},  # Tuyến bay từ Tân Sơn Nhất đến Hải Phòng
            {"dep_airport_id": 6, "des_airport_id": 7},  # Tuyến bay từ Hải Phòng đến Đà Lạt
            {"dep_airport_id": 7, "des_airport_id": 8},  # Tuyến bay từ Đà Lạt đến Quảng Ninh
            {"dep_airport_id": 8, "des_airport_id": 1}  # Tuyến bay từ Quảng Ninh về Tân Sơn Nhất
        ]

        for route in flight_routes:
            flight_route = FlightRoute(**route)
            db.session.add(flight_route)

        # Thêm dữ liệu vào bảng Flight
        flights = [
            {"flight_code": "VN123", "flight_route_id": 1, "airplane_id": 1},
            {"flight_code": "VJ456", "flight_route_id": 2, "airplane_id": 2},
            {"flight_code": "BB789", "flight_route_id": 3, "airplane_id": 3},
            {"flight_code": "VN101", "flight_route_id": 4, "airplane_id": 4},
            {"flight_code": "BB202", "flight_route_id": 5, "airplane_id": 5},
            {"flight_code": "VJ303", "flight_route_id": 1, "airplane_id": 6},
            {"flight_code": "BB57O", "flight_route_id": 1, "airplane_id": 7},
            {"flight_code": "A9125", "flight_route_id": 1, "airplane_id": 2}
        ]

        for flight in flights:
            f = Flight(**flight)
            db.session.add(f)

        # Thêm dữ liệu vào bảng FlightSchedule

        flight_schedules = [
            {
                "dep_time": datetime.datetime(2024, 12, 10, 8, 30),
                "flight_time": 120,
                "flight_id": 1,
                "business_class_seat_size": 15,
                "economic_class_seat_size": 55,
                "business_class_price": 1000000,
                "economic_class_price": 1500000
            },
            {
                "dep_time": datetime.datetime(2024, 12, 10, 10, 0),
                "flight_time": 90,
                "flight_id": 2,
                "business_class_seat_size": 25,
                "economic_class_seat_size": 60,
                "business_class_price": 2000000,
                "economic_class_price": 3000000
            },
            {
                "dep_time": datetime.datetime(2024, 12, 10, 12, 0),
                "flight_time": 80,
                "flight_id": 3,
                "business_class_seat_size": 20,
                "economic_class_seat_size": 70,
                "business_class_price": 1000000,
                "economic_class_price": 1500000
            },
            {
                "dep_time": datetime.datetime(2024, 12, 10, 15, 0),
                "flight_time": 100,
                "flight_id": 4,
                "business_class_seat_size": 15,
                "economic_class_seat_size": 50,
                "business_class_price": 1500000,
                "economic_class_price": 2000000
            },
            {
                "dep_time": datetime.datetime(2024, 12, 11, 8, 0),
                "flight_time": 130,
                "flight_id": 5,
                "business_class_seat_size": 30,
                "economic_class_seat_size": 60,
                "business_class_price": 4000000,
                "economic_class_price": 5500000
            },
            {
                "dep_time": datetime.datetime(2024, 12, 10, 14, 0),
                "flight_time": 95,
                "flight_id": 6,
                "business_class_seat_size": 20,
                "economic_class_seat_size": 45,
                "business_class_price": 1000000,
                "economic_class_price": 1500000
            },
            {
                "dep_time": datetime.datetime(2024, 12, 10, 10, 30),
                "flight_time": 115,
                "flight_id": 7,
                "business_class_seat_size": 15,
                "economic_class_seat_size": 45,
                "business_class_price": 1000000,
                "economic_class_price": 1500000
            },
            {
                "dep_time": datetime.datetime(2024, 12, 12, 17, 0),
                "flight_time": 120,
                "flight_id": 8,
                "business_class_seat_size": 10,
                "economic_class_seat_size": 55,
                "business_class_price": 1000000,
                "economic_class_price": 1500000
            }
        ]

        for schedule in flight_schedules:
            flight_schedule = FlightSchedule(**schedule)
            db.session.add(flight_schedule)
            db.session.commit()
            flight_schedule.create_seat_assignments()


        # Thêm dữ liệu vào bảng IntermediateAirport
        intermediate_airports = [
            {"airport_id": 3, "flight_id": 1, "stop_time": 30, "note": "Dừng đón khách"},
            # Dừng trung gian tại Đà Nẵng trong tuyến Tân Sơn Nhất - Nội Bài
            {"airport_id": 4, "flight_id": 2, "stop_time": 25, "note": "Chờ tiếp nhiên liệu"},
            # Dừng trung gian tại Vinh trong tuyến Nội Bài - Đà Nẵng
            {"airport_id": 2, "flight_id": 3, "stop_time": 40, "note": "Kiểm tra kỹ thuật"},
            # Dừng trung gian tại Nội Bài trong tuyến Đà Nẵng - Vinh
            {"airport_id": 1, "flight_id": 4, "stop_time": 35, "note": "Thay đổi phi hành đoàn"},
            # Dừng trung gian tại Tân Sơn Nhất trong tuyến Vinh - Cần Thơ
        ]

        for intermediate in intermediate_airports:
            inter_airport = IntermediateAirport(**intermediate)
            db.session.add(inter_airport)

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