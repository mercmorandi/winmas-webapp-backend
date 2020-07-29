from datetime import datetime, timedelta
from sqlalchemy import func, extract

from flask import current_app as app

from app import db
from app.models.locations import Location


class PosDto:
    def get_esps(self):
        return app.config["ESP_CONFIG"]["esp_list"]
