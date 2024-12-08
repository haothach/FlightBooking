from app.models import User, Province, Airport, Flight, FlightRoute
from app import app, db
import hashlib
import cloudinary.uploader
import sqlite3, pymysql


def load_province():
    return Province.query.order_by('name').all()


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
def load_flights(departure, destination, departure_date):
    conn = pymysql.connect(
        host='localhost',  # Địa chỉ máy chủ (thường là localhost)
        user='root',  # Tên người dùng MySQL
        password='123456',  # Mật khẩu người dùng
        database='flight',  # Tên cơ sở dữ liệu
    )
    cursor = conn.cursor()
    query = """
        SELECT 
            f.flight_code AS flight_code,  -- Mã chuyến bay
            t.ticket_class AS ticket_class,  -- Hạng vé
            dep_airport.name AS departure_airport,  -- Sân bay đi
            des_airport.name AS destination_airport,  -- Sân bay đến
            fs.dep_time AS departure_time,  -- Giờ khởi hành
            DATE_ADD(fs.dep_time, INTERVAL fs.flight_time MINUTE) AS arrival_time,  -- Giờ đến
            CASE 
                WHEN fs.flight_time < 60 THEN 
                    CONCAT(fs.flight_time, ' phút')  -- Chỉ hiển thị số phút
                ELSE 
                    CONCAT(
                        FLOOR(fs.flight_time / 60), ' giờ ',  -- Tính số giờ
                        MOD(fs.flight_time, 60), ' phút'      -- Tính số phút còn lại
                    )
            END AS flight_time,
            ap.name AS airplane_name,  -- Tên máy bay
            ap.airplane_type AS airline_name,  -- Tên hãng hàng không
            CASE 
                WHEN t.ticket_class = 1 THEN fs.first_class_ticket_price  -- Giá vé hạng nhất
                WHEN t.ticket_class = 2 THEN fs.second_class_ticket_price  -- Giá vé hạng phổ thông
            END AS ticket_price  -- Giá vé
        FROM 
            flight_schedule fs
        JOIN 
            flight f ON fs.flight_id = f.id
        JOIN 
            ticket t ON f.id = t.flight_id
        JOIN 
            flight_route fr ON f.flight_route_id = fr.id
        JOIN 
            airport dep_airport ON fr.dep_airport_id = dep_airport.id
        JOIN 
            airport des_airport ON fr.des_airport_id = des_airport.id
        JOIN 
            airplane ap ON f.airplane_id = ap.id
        JOIN 
            province dep_province ON dep_airport.province_id = dep_province.id
        JOIN 
            province des_province ON des_airport.province_id = des_province.id
        WHERE 
            dep_province.name = %s  -- Tên sân bay đi
            AND des_province.name = %s  -- Tên sân bay đến
            AND DATE(fs.dep_time) = %s;  -- Ngày khởi hành
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
            "ticket_class": row[1],  # Hạng vé
            "departure_airport": row[2],  # Sân bay đi
            "destination_airport": row[3],  # Sân bay đến
            "departure_time": row[4],  # Giờ khởi hành
            "arrival_time": row[5],  # Giờ đến
            "flight_time": row[6],  # Thời gian bay
            "airplane_name": row[7],  # Tên máy bay
            "airline_name": row[8],  # Tên hãng hàng không
            "ticket_price": row[9],  # Giá vé
        }
        for row in results
    ]

    return flights
