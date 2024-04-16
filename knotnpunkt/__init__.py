import logging
from os import (
    environ,
    path,
)
from pathlib import Path
from secrets import token_bytes
from alembic.config import Config
from alembic import command
from flask import Flask
from flask_login import LoginManager
from sqlalchemy import engine
from .database.db import (
    Benutzer,
)
from .site import site
from .api import api
from .utils import convertTime
from ._version import __version__
from ._update import check_current_head, apply_upgrade


def create_app(prevent_context_recursion: bool = False):
    """Flask app factory function:
    https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/

    Args:
        `prevent_context_recursion` (bool, optional): Set True to prevent calling
        a new app context. Used to fix a recursion error that was raised when
        applying db updates. Defaults to False.

    Returns:
        `flask.Flask`: The main app object
    """
    # Check if app is running in production and containerized and set instance path accordingly
    if not environ.get("FLASK_DEBUG") and environ.get('KP_DOCKER'):
        app = Flask(__name__, instance_path=Path(
            environ.get("KP_INSTANCE_PATH", "/data")).absolute())
        try:
            # Try to connect to gunicorns loggers
            gunicorn_logger = logging.getLogger('gunicorn.error')
            app.logger.handlers = gunicorn_logger.handlers
            app.logger.setLevel(gunicorn_logger.level)
        except:
            pass
        app.logger.info("knotnpunkt running containerized")
    else:
        app = Flask(__name__)
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-5.5s [%(name)s] %(message)s')
        app.logger.debug("knotnpunkt is running in debug mode")
    db_path = Path(app.instance_path) / "knotnpunkt.db"

    # Set secret key for signing
    app.secret_key = token_bytes(12)
    app.logger.info(f"Database file can be found at {db_path.absolute()}")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path.absolute()}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_DB_SEEDS_PATH'] = (
        Path(app.root_path) / "../migrations/seeds.py").absolute()
    # Load config concerning transaction-QR-Codes on Auslagen export
    app.config['KP_GIROCODE'] = environ.get('KP_GIROCODE', "true") == "true"
    app.logger.info(f"KP_GIROCODE={app.config['KP_GIROCODE']}")
    # Initializing alembic config needed for  migration-related commands
    alembic_cfg = Config(Path(app.root_path) / ".." / "alembic.ini")

    # Exploring existing db file and initializing the flask-sqlalchemy extension
    from knotnpunkt.database import db
    NEW_DB = not path.isfile(db_path)
    db.init_app(app)

    # Check database state
    if NEW_DB:
        # If DB is empty, seed it with ../migrations/seeds.py
        with app.app_context():
            app.logger.info(f"Seeding database at {db_path.absolute()}")
            db.create_all()
            command.stamp(alembic_cfg, "head")
            seeds_path = app.config.get("FLASK_DB_SEEDS_PATH")
            if path.exists(seeds_path):
                exec(open(seeds_path).read())
            else:
                app.logger.error(
                    "Could not seed database because of a missing file")
    elif not NEW_DB and not app.config.get('DEBUG') and not prevent_context_recursion:
        # If we have an existing database in production check for pending updates
        # If DEBUG=True, schema updates need to be applied by the `flask db` cli
        with app.app_context():
            app.logger.info(
                "Checking if database schema updates are available")
            e = engine.create_engine(f'sqlite:///{db_path.absolute()}')
            db_is_uptodate = check_current_head(alembic_cfg, e)
            if not db_is_uptodate:
                app.logger.info("Applying database schema updates")
                apply_upgrade(alembic_cfg)
            else:
                app.logger.info("Not database schema updates found")

    # Make convertTime available for all jinja templates
    app.jinja_env.globals.update(naturaltime=convertTime)

    # Register Blueprints
    app.register_blueprint(site)
    app.register_blueprint(api)

    # Initializing flask-login extension
    login_manager = LoginManager()
    login_manager.init_app(app)
    # Define Login page to redirect Unauthorized requests
    login_manager.login_view = "site.login"

    # Flask-login needs the user loader to get the users from the database
    @login_manager.user_loader
    def user_loader(user_id):
        return Benutzer.query.get(user_id)

    return app
