from flask import Flask
from flask_login import LoginManager
from secrets import token_bytes
from knotnpunkt.database import db
from .database.db import (
    Benutzer,
)
import logging
from . views import views  # Import routes to register as blueprints
# from .api import api 
from .utils import convertTime

app = Flask(__name__)
app.secret_key = token_bytes(12)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s: %(message)s')

app.jinja_env.globals.update(naturaltime=convertTime)

# Register Blueprints
app.register_blueprint(views)
# app.register_blueprint(api)


db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "views.login" # Define Login page to redirect Unauthorized requests


@login_manager.user_loader
def user_loader(user_id):
    return Benutzer.query.get(user_id)
