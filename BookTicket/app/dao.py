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
            tc.name AS ticket_class,
            dep_airport.name AS departure_airport,
            des_airport.name AS destination_airport,
            f.dep_time AS departure_time,
            f.flight_time AS flight_duration,
            DATE_ADD(fs.dep_time, INTERVAL f.flight_time MINUTE) AS arrival_time,
            ap.name AS airplane_name,
        CASE 
            WHEN t.ticket_class_id = 1 THEN fs.first_class_ticket_price
            WHEN t.ticket_class_id = 2 THEN fs.second_class_ticket_price
        END AS ticket_price
        FROM 
            ticket t
        JOIN 
            flight_schedule fs ON t.flight_id = fs.flight_id
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
        JOIN 
            ticket_class tc ON t.ticket_class_id = tc.id
        JOIN 
            province dep_province ON dep_airport.province_id = dep_province.id
        JOIN 
            province des_province ON des_airport.province_id = des_province.id
        WHERE 
            dep_province.name = %s 
            AND des_province.name = %s 
            AND DATE(fs.dep_time) = %s;

    """

    # Thực thi truy vấn
    cursor.execute(query, (departure, destination, departure_date))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Chuyển đổi kết quả thành danh sách dictionary
    flights = [
        {
            "ticket_class": row[0],  # Hạng vé (ticket_class)
            "dep_airport_name": row[1],  # Sân bay khởi hành
            "des_airport_name": row[2],  # Sân bay đến
            "departure_time": row[3],  # Giờ khởi hành
            "flight_duration": row[4],  # Thời gian bay
            "arrival_time": row[5],  # Giờ đến
            "airplane_name": row[6],  # Tên máy bay
            "ticket_price": row[7],  # Giá vé
        }
        for row in results
    ]

    return flights
