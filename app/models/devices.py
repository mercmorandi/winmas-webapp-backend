import datetime
from collections import namedtuple

from app import db


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(
        "id",
        db.Integer(),
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
    )
    last_update = db.Column("last_update", db.DateTime(), nullable=False, index=True)
    occurences = db.Column("occurrences", db.Integer(), nullable=False)
    mac = db.Column(
        "MAC", db.String(length=255), nullable=False, primary_key=True, unique=True
    )
    locations = db.relationship(
        "Location", back_populates="device", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return str(self.id) + " - " + self.mac + " - " + str(self.last_update)

    def set_last_update(self, probe_ts):
        self.last_update = datetime.datetime.fromtimestamp(probe_ts)


DeviceDTO = namedtuple("DeviceDTO", "id, mac, last_update, occurences, locations")


def toDeviceDTO(device):
    pos = [
        {"x": loc.x, "y": loc.y, "date": loc.insertion_date.isoformat(), "ssid": loc.ssid} for loc in device.locations
    ]
    return dict(
        DeviceDTO(
            id=device.id,
            mac=device.mac,
            last_update=device.last_update.isoformat(),
            occurences=device.occurences,
            locations=pos,
        )._asdict()
    )


def serve_device_info(device_id):
    qs = db.session.query(Device).filter(Device.id == device_id)
    return toDeviceDTO(qs.first()) if qs.first() else {}
