
from app.models import User, Province, Airport, Flight, FlightRoute,FlightSchedule,Ticket
from app import app, db
import hashlib
import cloudinary.uploader
import sqlite3, pymysql
import datetime


def load_province():
    return Province.query.order_by('name').all()


def load_airport():
    return Airport.query.order_by('id').all()


def load_flight():
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


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()


def get_user_by_id(id):
    return User.query.get(id)


# function connect to database
def load_flights(departure, destination, departure_date):
    conn = pymysql.connect(
        host='localhost',  # Địa chỉ máy chủ (thường là localhost)
        user='root',  # Tên người dùng MySQL
        password='123456',  # Mật khẩu người dùng
        database='flight',  # Tên cơ sở dữ liệu
    )
    cursor = conn.cursor()
    query = """
        WITH RankedAirports AS (
            SELECT 
                f.flight_code,
                ia.airport_id,
                a.name AS airport_name,
                ia.stop_time,
                ROW_NUMBER() OVER (PARTITION BY f.flight_code ORDER BY ia.stop_time) AS rn
            FROM 
                flight f
            LEFT JOIN 
                intermediate_airport ia ON f.id = ia.flight_id
            LEFT JOIN 
                airport a ON ia.airport_id = a.id
            WHERE 
                ia.stop_time IS NOT NULL
        )
        SELECT 
            f.flight_code,  -- Mã chuyến bay,
            fs.business_class_price AS business_price,  -- Giá vé hạng 1
            fs.economy_class_price AS economy_price,  -- Giá vé hạng 2
            dep_airport.name AS departure_airport,  -- Sân bay đi
            des_airport.name AS destination_airport,  -- Sân bay đến
            fs.dep_time AS departure_time,  -- Giờ khởi hành
            DATE_ADD(fs.dep_time, INTERVAL fs.flight_time MINUTE) AS arrival_time,  -- Giờ đến (tính từ giờ khởi hành + thời gian bay)
            CASE 
                WHEN fs.flight_time < 60 THEN 
                    CONCAT(fs.flight_time, ' phút')
                ELSE 
                    CONCAT(
                        FLOOR(fs.flight_time / 60), ' giờ ',
                        LPAD(MOD(fs.flight_time, 60), 2, '0'), ' phút'
                    )
            END AS flight_time,
            ap.name AS airplane_name,  -- Tên máy bay
            ap.airplane_type AS airline_name,  -- Tên hãng hàng không
            (SELECT COUNT(*) 
             FROM seat_assignment sa
             JOIN seat s ON sa.seat_id = s.id
             WHERE sa.flight_schedule_id = fs.id AND sa.is_available = 1 AND s.seat_class = 1) AS remaining_business_seats,  -- Số ghế hạng 1 còn lại
            (SELECT COUNT(*) 
             FROM seat_assignment sa
             JOIN seat s ON sa.seat_id = s.id
             WHERE sa.flight_schedule_id = fs.id AND sa.is_available = 1 AND s.seat_class = 2) AS remaining_economy_seats,
            f.id,
            MAX(CASE WHEN rn = 1 THEN ra.airport_name END) AS intermediate_airport_1,  -- Tên sân bay trung gian 1
            MAX(CASE WHEN rn = 2 THEN ra.airport_name END) AS intermediate_airport_2,  -- Tên sân bay trung gian 2
            MAX(CASE WHEN rn = 1 THEN ra.stop_time END) AS ia_stop_time_1,  -- Thời gian dừng trung gian 1
            MAX(CASE WHEN rn = 2 THEN ra.stop_time END) AS ia_stop_time_2   -- Thời gian dừng trung gian 2
  
        FROM 
            flight_schedule fs
        JOIN 
            flight f ON fs.flight_id = f.id
        JOIN 
            flight_route fr ON f.flight_route_id = fr.id
        JOIN 
            airport dep_airport ON fr.dep_airport_id = dep_airport.id
        JOIN 
            airport des_airport ON fr.des_airport_id = des_airport.id
        JOIN 
            airplane ap ON f.airplane_id = ap.id
        LEFT JOIN 
            intermediate_airport ia ON f.id = ia.flight_id
        LEFT JOIN 
            airport a ON ia.airport_id = a.id
        LEFT JOIN 
            RankedAirports ra ON f.flight_code = ra.flight_code
        LEFT JOIN 
            seat_assignment sa ON sa.flight_schedule_id = fs.id
        JOIN 
            province dep_province ON dep_airport.province_id = dep_province.id
        JOIN 
            province des_province ON des_airport.province_id = des_province.id
        WHERE 
            dep_province.name = %s  -- Tên tỉnh sân bay đi
            AND des_province.name = %s  -- Tên tỉnh sân bay đến
            AND DATE(fs.dep_time) = %s  -- Ngày khởi hành
        GROUP BY 
            f.flight_code, fs.business_class_price, fs.economy_class_price, dep_airport.name, des_airport.name, 
            fs.dep_time, fs.flight_time, ap.name, ap.airplane_type, f.id;


    """
    # Thực thi truy vấn
    cursor.execute(query, (departure, destination, departure_date))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Chuyển đổi kết quả thành danh sách dictionary
    flights = [
        {
            "flight_code": row[0],  # Mã chuyến bay
            "business_price": row[1],  # Giá vé hạng 1
            "economy_price": row[2],  # Giá vé hạng 2
            "departure_airport": row[3],  # Sân bay đi
            "destination_airport": row[4],  # Sân bay đến
            "departure_time": row[5],  # Giờ khởi hành
            "arrival_time": row[6],  # Giờ đến
            "flight_time": row[7],  # Thời gian bay
            "airplane_name": row[8],  # Tên máy bay
            "airline_name": row[9],  # Tên hãng hàng không
            "remaining_business_seats": row[10],  # Thời gian dừng
            "remaining_economy_seats": row[11],  # Số ghế hạng 1 còn lại
            "flight_id": row[12],  # Số ghế hạng 2 còn lại
            "intermediate_airport_1":row[13],
            "intermediate_airport_2":row[14],
            "ia_stop_time_1":row[15],
            "ia_stop_time_2":row[16]
        }
        for row in results
    ]

    return flights


