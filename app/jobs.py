import time
import datetime
import requests
import json

from app import db, tasks
from celery.utils.log import get_task_logger
from .models.probes import Probe
from .models.locations import Location
from .models.devices import Device
from app import archimede
from flask import current_app as app

logger = get_task_logger(__name__)


def trilateration_job(p_hash):
    qs = db.session.query(Probe).filter(Probe.hash == p_hash)
    rssi_dict = {p.esp_id: p.signal_strength_wroom for p in qs.all()}
    probes = qs.all()
    x, y = archimede.trilaterator(rssi_dict)

    current_mac = probes[0].source
    print("current_mac: " + current_mac)
    device = None
    if not db.session.query(Device).filter(Device.mac == current_mac).all():
        print("nuovo device")
        device = Device(
            last_update=datetime.datetime.fromtimestamp(probes[0].timestamp),
            occurences=0,
            mac=current_mac,
        )
    else:
        print("device gia recorded")
        # maybe use session
        device = Device.query.filter(Device.mac == current_mac).all()[0]
        device.set_last_update(probes[0].timestamp)

    location = Location(
        hash=p_hash,
        ssid=probes[0].ssid,
        insertion_date=datetime.datetime.fromtimestamp(probes[0].timestamp),
        x=x,
        y=y,
        mac_id=current_mac,
        device=device,
    )
    device.locations.append(location)
    device.occurences = device.occurences + 1
    db.session.add(location)
    db.session.add(device)
    print(str(location))
    print(str(device))

    db.session.commit()
    res = {
        "mac": location.mac_id,
        "ssid": location.ssid,
        "insertion_date": location.insertion_date.isoformat(),
        "x": location.x,
        "y": location.y,
    }
    requests.post("http://backend:5000/new_location_event", json=res)
    db.session.close()
    return "trilaterator task done"


def trilaterable_check_job(p_hash):
    qs = db.session.query(Probe).filter(Probe.hash == p_hash)
    if qs.count() == int(app.config["NUMESP"]):
        print("trilaterable probe found")
        qs.update({Probe.status: "pending"})
        db.session.commit()
        tasks.trilateration_task.delay(p_hash)
    else:
        print("not trilaterable probe")

    db.session.close()


def discardable_check_job():
    for probe in (
        db.session.query(Probe)
        .filter(Probe.status == "unchecked")
        .filter(time.time() - Probe.timestamp > 120)
    ):
        probe.status = "discarded"

    db.session.commit()
