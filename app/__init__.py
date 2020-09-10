from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from config import Config
from celery import Celery
from .celery_utils import init_celery
from celery.schedules import crontab

import yaml

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object("config.Config")
    print("config loaded")
    print(str(app.config))
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins='*')


    # CELERY
    app.config["CELERYBEAT_SCHEDULE"] = {
        # Executes every minute
        "periodic_task-every-minute": {
            "task": "filter_task",
            "schedule": crontab(minute="*"),
        }
    }

    try:
        with open("esp_config.yaml", "r") as f:
            app.config["ESP_CONFIG"] = yaml.load(f)
    except Exception as e:
        print(e)
        exit(-1)

    init_celery(celery, app)

    with app.app_context():
        # Imports
        from . import routes
        from . import db_connection

        # Da usare in shell: flask_app.app_context().push()

    return app
