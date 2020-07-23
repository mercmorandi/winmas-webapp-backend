import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from celery import Celery
from .celery_utils import init_celery
from celery.schedules import crontab

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object("config.Config")
    print("config loaded")
    # print(str(app.config))
    db.init_app(app)
    migrate.init_app(app, db)

    # CELERY
    app.config["CELERYBEAT_SCHEDULE"] = {
        # Executes every minute
        "periodic_task-every-minute": {
            "task": "filter_task",
            "schedule": crontab(minute="*"),
        }
    }

    init_celery(celery, app)

    with app.app_context():
        # Imports
        from . import routes
        from . import db_connection

        # Da usare in shell: flask_app.app_context().push()

    return app
