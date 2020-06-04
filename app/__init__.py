import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from celery import Celery
from .celery_utils import init_celery

db = SQLAlchemy()
migrate = Migrate()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    print("config loaded")
    # print(str(app.config))
    db.init_app(app)
    migrate.init_app(app, db)

    # CELERY
    init_celery(celery, app)

    with app.app_context():
        # Imports
        from . import routes
        from . import db_connection
        # from .models import probes, locations, devices

        # db = db_connection.DBConnection()
        # print("Established connection to db...")  #for debugging
        # db.create_tables()
        # print("Created database tables")  #for debugging
        ##clear any lingering data and start afresh
        # db.clear_data()

    return app
