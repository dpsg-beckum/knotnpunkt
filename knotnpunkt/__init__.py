from flask import Flask
from flask_login import LoginManager
from secrets import token_bytes
from knotnpunkt.database import db
from .database.db import (
    Benutzer,
)
import logging
from . views import views  # Import routes to register as blueprints
from .api import api 
from .utils import convertTime
from ._version import __version__
app = Flask(__name__)
app.secret_key = token_bytes(12)

if environ.get('KP_DOCKER'):
    db_path = Path(environ.get("KP_DATABASE_PATH", "/data/database.db"))
    RUN_DB_SETUP = not path.isfile(db_path)
    print(db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path.absolute()}'
else:
    db_path = Path(getcwd()) / "database.db"
    print(db_path.absolute())
    RUN_DB_SETUP = not path.isfile(db_path)
    print(db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path.absolute()}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s: %(message)s')

app.jinja_env.globals.update(naturaltime=convertTime)

# Register Blueprints
app.register_blueprint(views)
app.register_blueprint(api)


db.init_app(app)
if RUN_DB_SETUP:
    with app.app_context():
        db.create_all()
        for i in initial_data.get('Rolle'):
            db.session.add(i)
            db.session.commit()
        for i in initial_data.get('Label'):
            db.session.add(i)
            db.session.commit()
        for i in initial_data.get('Kategorie'):
            db.session.add(i)
            db.session.commit()
        for i in initial_data.get('Benutzer'):
            db.session.add(i)
            db.session.commit()
        RUN_DB_SETUP = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "views.login"  # Define Login page to redirect Unauthorized requests


@login_manager.user_loader
def user_loader(user_id):
    return Benutzer.query.get(user_id)
