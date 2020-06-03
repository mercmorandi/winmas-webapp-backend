from sqlalchemy.orm import relationship
#from flask import current_app as app

#db = app.db
from app import db
import enum

class StatusEnum(enum.Enum):
    unchecked = 0
    tracked = 1
    discarded = 2
    


class Probe(db.Model):

    __tablename__ = "probes"

    id = db.Column(
        "id", db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    timestamp = db.Column("timestamp", db.Integer(), nullable=False)
    destination = db.Column("destination", db.String(length=255), nullable=False)
    source = db.Column("source", db.String(length=255), nullable=False)
    bssid = db.Column("bssid", db.String(length=255))
    ssid = db.Column("ssid", db.String(length=255))
    signal_strength_wroom = db.Column(
        "signal_strength_wroom", db.Integer(), nullable=False
    )
    signal_strength_rt = db.Column("signal_strength_rt", db.Integer(), nullable=False)
    hash = db.Column("HASH", db.String(length=255), nullable=False)
    device_id = db.Column('device_id', db.String(length=255), nullable=False)
    #status = db.Column('status', db.Enum(StatusEnum), nullable = False)
    #status = db.Enum('unchecked', 'tracked', 'discarded', name='probe_status')
    status = db.Column('probe_status', db.Enum('unchecked', 'tracked', 'discarded',name='probe_status'), nullable=False)

    def __init__(self, destination, source, bssid, ssid, signal_strength_wroom, signal_strength_rt, hash, timestamp, device_id):
        self.destination = destination
        self.source = source
        self.bssid = bssid
        self.signal_strength_rt = signal_strength_rt
        self.signal_strength_wroom = signal_strength_wroom
        self.hash = hash
        self.timestamp = timestamp
        self.device_id = device_id
        self.status = 'unchecked'
    # mocked probe
    # "timestamp":"565",
    # "destination":"ff:ff:ff:ff:ff:ff",
    # "source":"00:19:88:15:6d:5e",
    # "bssid":"ff:ff:ff:ff:ff:ff",
    # "ssid":"pib1",
    # "signal_strength_wroom":"-88",
    # "signal_strength_rt":"109"
