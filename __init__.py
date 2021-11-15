import os
from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2 import WebApplicationClient

# If your server is not parametrized to allow HTTPS,
# the fetch_token method will raise an "oauthlib.oauth2.rfc6749.errors.InsecureTransportError".
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:tuan0512@localhost/clinic_db?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "my@clinic.com"

# Configuration
GOOGLE_CLIENT_ID = "919352421263-e18mqjhotmb6l176kflviroomrbbd5qd.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

db = SQLAlchemy(app=app)
admin = Admin(app=app, name='CLINIC', template_mode='bootstrap4')
my_login = LoginManager(app)
# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)
