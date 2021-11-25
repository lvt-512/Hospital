import os
from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
from oauthlib.oauth2 import WebApplicationClient
from flask_mail import Mail

# If your server is not parametrized to allow HTTPS,
# the fetch_token method will raise an "oauthlib.oauth2.rfc6749.errors.InsecureTransportError".
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:tuan0512@localhost/clinic_db?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "my@clinic.com"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'temporaryleo0512@gmail.com'
app.config['MAIL_PASSWORD'] = 'tuan0512@'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = ('MedAll', 'temporaryleo0512@gmail.com')

# Configuration
GOOGLE_CLIENT_ID = "919352421263-e18mqjhotmb6l176kflviroomrbbd5qd.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

BOOKING_MAX = 2

db = SQLAlchemy(app=app)
admin = Admin(app=app, name='CLINIC', template_mode='bootstrap4')
my_login = LoginManager(app)
client = WebApplicationClient(GOOGLE_CLIENT_ID)  # OAuth 2 client setup
mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

