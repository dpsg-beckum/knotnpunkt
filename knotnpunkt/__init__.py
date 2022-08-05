from flask import Flask
from flask_login import LoginManager
from secrets import token_bytes
from .models import *
from .views import views

app = Flask(__name__)
app.secret_key = token_bytes(12)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.jinja_env.globals.update(naturaltime=util)

app.register_blueprint(views)
# app.register_blueprint(api)

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)    


@login_manager.user_loader
def user_loader(user_id):
    return Benutzer.query.get(user_id)