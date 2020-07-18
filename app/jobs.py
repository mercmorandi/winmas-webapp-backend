import itertools
import time
import datetime

from app import db, tasks
from celery.utils.log import get_task_logger
from sqlalchemy import func
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
            last_update=datetime.datetime.fromtimestamp(probes[0].timestamp / 1000),
            occurences=0,
            mac=current_mac,
        )
    else:
        print("device gia recorded")
        device = Device.query.filter(Device.mac == current_mac).all()[0]
        device.set_last_update(probes[0].timestamp)

    location = Location(
        hash=p_hash,
        ssid=probes[0].ssid,
        insertion_date=datetime.datetime.fromtimestamp(probes[0].timestamp / 1000),
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
    db.session.close()
    return "trilaterator task done"


def trilaterable_check_job(p_hash):
    qs = db.session.query(Probe).filter(Probe.hash == p_hash)
    if len(qs.all()) == int(app.config["NUMESP"]):
        print('trilaterable probe found')
        for p in qs.all():
            p.status = "pending"
        db.session.commit()
        tasks.trilateration_task.delay(p_hash)
    else:
        print('not trilaterable probe')

    db.session.close()


def discardable_check_job():
    qs = (
        db.session.query(Probe)
            .filter(Probe.status == "unchecked")
            .filter(time.time() - (Probe.timestamp / 1000) > 2)
    )

    for p in qs.all():
        p.status = 'discarded'

    db.session.commit()
