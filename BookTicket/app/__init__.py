from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
import cloudinary
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = 'thachnhsdfasdfgqw'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/flight?charset=utf8mb4" % quote("123456")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

cloudinary.config(cloud_name='dnoubiojc',
                  api_key='719948317126525',
                  api_secret='CHYBjymue2PW038ILQrwUQD6XfY')

login = LoginManager(app)