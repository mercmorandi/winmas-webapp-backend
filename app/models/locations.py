from collections import namedtuple
from sqlalchemy import func

from app import db
from app.utils import date_parser


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
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"))
    device = db.relationship("Device", back_populates="locations")

    def __repr__(self):
        return (
            str(self.id)
            + " - "
            + self.hash
            + " - "
            + str(self.x)
            + " - "
            + str(self.y)
            + " - "
            + str(self.insertion_date)
            + " - "
            + str(self.device)
        )


LocationDTO = namedtuple(
    "LocationDTO", "id, ssid, insertion_date, x, y, mac, device_id"
)


def to_locationDTO_dict(qs):
    res = [
        dict(
            LocationDTO(
                id=loc.id,
                ssid=loc.ssid,
                insertion_date=loc.insertion_date.replace(microsecond=0).isoformat(),
                x=loc.x,
                y=loc.y,
                mac=loc.mac_id,
                device_id=loc.device_id,
            )._asdict()
        )
        for loc in qs
    ]

    return res


def serve_last_locations(request):
    start_date = date_parser(request.args.get("start_date"))
    end_date = date_parser(request.args.get("end_date"))
    qs1 = (
        db.session.query(
            Location.id, func.max(Location.insertion_date).label("max_date")
        )
        .filter(Location.insertion_date >= start_date)
        .filter(Location.insertion_date < end_date)
        .group_by(Location.id)
        .distinct(Location.mac_id)
        .subquery()
    )

    qs = db.session.query(Location).join(qs1, Location.id == qs1.c.id).order_by(Location.device_id)

    res = to_locationDTO_dict(qs)
    db.session.close()

    return res


def serve_active_locations(request):
    start_date = date_parser(request.args.get("start_date"))
    end_date = date_parser(request.args.get("end_date"))
    qs = (
        db.session.query(Location)
        .filter(Location.insertion_date >= start_date)
        .filter(Location.insertion_date < end_date)
    )
    res = to_locationDTO_dict(qs)
    db.session.close()

    return res
