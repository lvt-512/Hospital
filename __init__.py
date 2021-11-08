from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:tuan0512@localhost/clinic_db?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "@#$%^&%&&^@**(*(!("

db = SQLAlchemy(app=app)
admin = Admin(app=app, name='CLINIC', template_mode='bootstrap4')
my_login = LoginManager(app)
