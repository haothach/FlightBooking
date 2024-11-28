from app.models import User, Province, Airport, Flight, FlightRoute
from app import app, db
import hashlib
import cloudinary.uploader
import sqlite3, pymysql


def load_province():
    return Province.query.order_by('id').all()


def load_flight_route():
    return Flight.query.order_by('id').all()


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
def query_database(departure, destination, departure_date):
    conn = pymysql.connect(
        host='localhost',  # Địa chỉ máy chủ (thường là localhost)
        user='root',  # Tên người dùng MySQL
        password='123456',  # Mật khẩu người dùng
        database='flight',  # Tên cơ sở dữ liệu
    )
    cursor = conn.cursor()
    query = """
        SELECT 
            CASE 
                WHEN fs.first_class_ticket_price IS NOT NULL THEN 'Hạng 1'
                ELSE 'Hạng 2'
            END AS ticket_class,
            TIME(fs.dep_date) AS departure_time,
            CONCAT(FLOOR(fs.flight_time / 60), ' giờ ', MOD(fs.flight_time, 60), ' phút') AS flight_duration,
            TIME(DATE_ADD(fs.dep_date, INTERVAL fs.flight_time MINUTE)) AS arrival_time, 
            dep_airport.name AS departure_airport, 
            des_airport.name AS destination_airport, 
            a.airplane_type AS airline, 
            fs.first_class_ticket_price AS first_class_price,
            fs.second_class_ticket_price AS second_class_price 
        FROM flight_schedule fs  
        JOIN flight f ON fs.flight_id = f.id
        JOIN flight_route fr ON f.flight_route_id = fr.id
        JOIN airport dep_airport ON fr.dep_airport_id = dep_airport.id
        JOIN airport des_airport ON fr.des_airport_id = des_airport.id
        JOIN province dep_province ON dep_airport.province_id = dep_province.id -- Thêm JOIN bảng province (sân bay đi)
        JOIN province des_province ON des_airport.province_id = des_province.id -- Thêm JOIN bảng province (sân bay đến)
        JOIN airplane a ON f.airplane_id = a.id
        WHERE dep_province.name = %s -- Thêm điều kiện tỉnh đi
          AND des_province.name = %s -- Thêm điều kiện tỉnh đến
          AND DATE(fs.dep_date) = %s
    """

    # Thực thi truy vấn
    cursor.execute(query, (departure, destination, departure_date))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Chuyển đổi kết quả thành danh sách dictionary
    flights = [
        {
            "ticket_class": row[0],
            "departure_time": row[1],
            "flight_duration": row[2],
            "arrival_time": row[3],
            "dep_airport_name": row[4],
            "des_airport_name": row[5],
            "airline": row[6],
            "first_class_price": row[7],
            "second_class_price": row[8],
        }
        for row in results
    ]

    return flights
