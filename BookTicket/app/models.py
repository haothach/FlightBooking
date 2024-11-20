from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app import db, app
import hashlib
from enum import Enum as RoleEnum
from flask_login import UserMixin


class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    STAFF = 3


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

    def __str__(self):
        return self.name


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # u = User(name="admin", username="admin", password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
        #          avatar="https://res.cloudinary.com/dnoubiojc/image/upload/v1731852091/cld-sample-5.jpg",
        #          user_role=UserRole.ADMIN)
        # db.session.add(u)
        #
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
        }]

        for p in provinces:
            p = Province(**p)
            db.session.add(p)

        airports = [{
            "name": "Tân Sơn Nhất",
            "add": "Phường 2, 4 và 15, Quận Tân Bình",
            "province_id": 1
        }, {
            "name": "Cam Ranh",
            "add": "đường Nguyễn Tất Thành, thành phố Cam Ranh, tỉnh Khánh Hòa",
            "province_id": 1
        }]

        for a in airports:
            a = Airport(**a)
            db.session.add(a)

        db.session.commit()
