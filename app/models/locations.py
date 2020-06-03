from sqlalchemy.orm import relationship
#from flask import current_app as app

#db = app.db
from app import db

class Location(db.Model):

    __tablename__ = "locations"

    id = db.Column(
        "id", db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    hash = db.Column("HASH", db.String(length=255), nullable=False)
    ssid = db.Column("SSID", db.String(length=255), nullable=False)
    insertion_date = db.Column("insertion_date", db.DateTime(), nullable=False)
    x = db.Column("x", db.Integer(), nullable=False)
    y = db.Column("y", db.Integer(), nullable=False)
    mac_id = db.Column("MAC_id", db.String(length=255), nullable=False)
    device = relationship("Devices", backref="devices")
