import itertools
import time
import datetime

from app import celery, db
from celery.utils.log import get_task_logger
from sqlalchemy import func
from .models.probes import Probe
from .models.locations import Location
from .models.devices import Device
from flask import current_app as app

logger = get_task_logger(__name__)


@celery.task
def add(a, b):
    return a + b


@celery.task(name="periodic_task")
def periodic_task():
    print("Hi! from periodic_task")
    logger.info("Hello! from periodic task")
    return "ciao"


@celery.task(name="filter_task")
def filter_task():
    logger.info(str(db.session))

    q1 = (
        db.session.query(
            Probe.hash,
            Probe.source,
            Probe.timestamp / 1000 / 60,
            func.count(Probe.hash).label("probe_count"),
        )
            .group_by(Probe.hash, Probe.source, Probe.timestamp / 1000 / 60)
            .filter(Probe.status == "unchecked")
    ).subquery()
    # .having(func.count(Probe.hash) == 3)
    q2 = Probe.query.join(q1, Probe.hash == q1.c.HASH)
    if not q2:
        logger.info("all probes are checked")
        return "done"

    def key_func(a):
        return a.hash

    def key_func2(a):
        return a.esp_id

    for key, group in itertools.groupby(q2.all(), key_func):
        l = list(group)
        print(key + " :", str(l))
        # print(list(group))
        p_minutes = int(l[0].timestamp / 1000 / 60)
        now_minutes = int(time.time() / 60)
        how_old = now_minutes - p_minutes
        if len(l) < int(app.config["NUMESP"]) and how_old > 2:
            for p in l:
                print("dicarded1")
                p.status = "discarded"
        elif len(l) >= int(app.config["NUMESP"]):
            ids = {p.device_id for p in l}
            print(str(ids))
            print(str(app.config["NUMESP"]))
            print(str(len(ids)))
            if len(ids) != int(app.config["NUMESP"]) and how_old > 2:
                for p in l:
                    print("dicarded2")
                    p.status = "discarded"  # ritrasmissione
            # elif len(l) > int(
            #    app.config["NUMESP"]
            # ):  # rimuove probe ricevute piu di una volta dallo stesso esp
            else:
                # si puo evitare mettendo unique constraint su esp_id e hash
                # e catturare l'eccezione in routes
                for key2, group2 in itertools.groupby(l, key_func2):
                    l2 = list(group2)
                    if len(l2) > 1:
                        print("pending1")
                        l2[0].status = "pending"
                        for p in l2[1:]:
                            print("dicarded3")
                            p.status = "discarded"

                    else:
                        print("pending2")
                        l2[0].status = "pending"
        else:
            for p in l:
                print("pending3")
                p.status = "pending"

    db.session.commit()

    return "done"


@celery.task(name="trilateration_task")
def trilateration_task():
    q1 = (
        db.session.query(
            Probe.source,
            Probe.timestamp / 1000 / 60,
            Probe.hash,
            func.count(Probe.hash).label("probe_count"),
        )
            .group_by(Probe.source, Probe.timestamp / 1000 / 60, Probe.hash)
            .filter(Probe.status == "pending")
    ).subquery()

    q2 = Probe.query.join(q1, Probe.hash == q1.c.HASH).filter(Probe.status == "pending")

    def key_func(a):
        return a.hash

    for key, group in itertools.groupby(q2.all(), key_func):
        l = list(group)
        print(key + " :", str(l))
        rssi_dict = {p.esp_id: p.signal_strength_wroom for p in l}
        x, y = trilaterator(rssi_dict)
        current_mac = l[0].source
        print('current_mac: '+current_mac)
        device = None
        if not db.session.query(Device).filter(Device.mac == current_mac).all():
            print('nuovo device')
            device = Device(
                last_update=datetime.datetime.fromtimestamp(l[0].timestamp / 1000),
                occurences=0,
                mac=current_mac,
            )
        else:
            print('device gia recorded')
            device = Device.query.filter(Device.mac == current_mac).all()[0]
            device.set_last_update(l[0].timestamp)

        location = Location(
            hash=key,
            ssid=l[0].ssid,
            insertion_date=datetime.datetime.fromtimestamp(l[0].timestamp / 1000),
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
    return "triangular task done"


def trilaterator(rssi_dict):
    data_dict = {
        esp_id: (
            compute_distance(rssi),
            int(app.config["X" + esp_id[-1:]]),
            int(app.config["Y" + esp_id[-1:]]),
        )
        for esp_id, rssi in rssi_dict.items()
    }

    print(str(data_dict))

    x_a = data_dict['EspWroom01'][1]
    x_b = data_dict['EspWroom02'][1]
    x_c = data_dict['EspWroom03'][1]
    y_a = data_dict['EspWroom01'][2]
    y_b = data_dict['EspWroom02'][2]
    y_c = data_dict['EspWroom03'][2]
    d_a = data_dict['EspWroom01'][0]
    d_b = data_dict['EspWroom02'][0]
    d_c = data_dict['EspWroom03'][0]

    v_a = (
                  (x_c ** 2 - x_b ** 2)
                  + (y_c ** 2 - y_b ** 2)
                  + (d_b ** 2 - d_c ** 2)
          ) / 2

    v_b = (
                  (x_a ** 2 - x_b ** 2)
                  + (y_a ** 2 - y_b ** 2)
                  + (d_b ** 2 - d_a ** 2)
          ) / 2

    y = (
                v_b * (x_b - x_c)
                - v_a * (x_b - x_a)
        ) / (
                (y_a - y_b) * (x_b - x_c)
                - (y_c - y_b) * (x_b - x_c)
        )

    x = (y * (y_a - y_b) - v_b) / (
            x_b - x_c
    )
    print('x: '+str(x)+' y: '+str(y))
    return x, y


def compute_distance(rssi):
    # distance = 10 ** (
    #        (int(app.config["ESP_MES_POWER"]) - rssi) / 10 * int(app.config["ENV_FACTOR"])
    # )
    a = int(app.config["ESP_MES_POWER"])
    n = int(app.config["ENV_FACTOR"])
    distance = 10 ** ((a - rssi) / (n * 10))
    return distance
