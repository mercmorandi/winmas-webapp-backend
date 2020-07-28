from sqlalchemy.orm import relationship
import  time
# from flask import current_app as app

# db = app.db
from app import db

from hashlib import md5


class Probe(db.Model):
    __tablename__ = "probes"

    id = db.Column(
        "id", db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    timestamp = db.Column(
        "timestamp", db.BigInteger(), nullable=False
    )  # unix timestamp (utc in millisecond)
    seqnum = db.Column("seqnum", db.Integer())
    destination = db.Column("destination", db.String(length=255), nullable=False)
    source = db.Column("source", db.String(length=255), nullable=False)
    bssid = db.Column("bssid", db.String(length=255))
    ssid = db.Column("ssid", db.String(length=255))
    signal_strength_wroom = db.Column(
        "signal_strength_wroom", db.Integer(), nullable=False
    )
    signal_strength_rt = db.Column("signal_strength_rt", db.Integer(), nullable=False)
    hash = db.Column(
        "HASH", db.String(length=255), nullable=False
    )  # calcolato sul minuto approssimato da timestamp
    esp_id = db.Column("esp_id", db.String(length=255), nullable=False)
    status = db.Column(
        "probe_status",
        db.Enum("unchecked", "pending", "tracked", "discarded", name="probe_status"),
        nullable=False,
    )
    __table_args__ = (db.UniqueConstraint("HASH", "esp_id", name="_hash_esp_id_uc"),)

    def __repr__(self):
        return (
                str(self.id)
                + " - "
                + self.source
                + " - "
                + self.esp_id
                + " - "
                + str(self.timestamp)
                + " - "
                + str(self.status)
        )

    # mocked probe
    # "timestamp":"565",
    # "destination":"ff:ff:ff:ff:ff:ff",
    # "source":"00:19:88:15:6d:5e",
    # "bssid":"ff:ff:ff:ff:ff:ff",
    # "ssid":"pib1",
    # "signal_strength_wroom":"-88",
    # "signal_strength_rt":"109"


# p = Probe.query.filter(Probe.hash == '0a6fe86e018738b08db53b545e348f8c')
# rssi_dict = {'EspWroom01': -83, 'EspWroom02': -72, 'EspWroom03': -74}

def probe_parser(req):
    device_id = req["device_id"]
    on_since = int(req["on_since"])
    probe = req["probe"]

    ts = int(round(time.time() * 1000)) - (on_since - int(probe["timestamp"]))
    minutes_ts = int(ts / 1000 / 60)
    to_encode = (
            probe["destination"]
            + ""
            + probe["source"]
            + ""
            + str(minutes_ts)
            + ""
            + probe["seq_number"]
    )
    h = md5(to_encode.encode("utf-8")).hexdigest()
    print("HASSSSSSSSH: " + str(h))
    probe = Probe(
        destination=probe["destination"],
        source=probe["source"],
        bssid=probe["bssid"],
        ssid=probe["ssid"],
        signal_strength_wroom=probe["signal_strength_wroom"],
        signal_strength_rt=probe["signal_strength_rt"],
        hash=str(h),
        timestamp=ts,
        seqnum=probe["seq_number"],
        esp_id=device_id,
        status="unchecked",
    )
