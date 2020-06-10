from sqlalchemy.orm import relationship

# from flask import current_app as app

# db = app.db
from app import db


class Device(db.Model):

    __tablename__ = "devices"

    id = db.Column(
        "id", db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    last_update = db.Column("last_update", db.DateTime(), nullable=False, index=True)
    occurences = db.Column("occurrences", db.Integer(), nullable=False)
    mac = db.Column(
        "MAC", db.String(length=255), nullable=False, primary_key=True, unique=True
    )
    locations = relationship("Location", backref="locations")
