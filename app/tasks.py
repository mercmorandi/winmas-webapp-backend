import time

from app import celery, db
from celery.utils.log import get_task_logger
from sqlalchemy import func
from .models.probes import Probe
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
    q = (
        db.session.query(Probe.hash, func.count(Probe.hash).label("probe_count"))
            .group_by(Probe.hash)
            .subquery()
    )
    q2 = (
        Probe.query.join(q, Probe.hash == q.c.HASH)
            .filter(Probe.status == "unchecked")
            .filter(q.c.probe_count == app.config["NUMESP"])
            .order_by(Probe.timestamp.desc())
    )
    logger.info(q2.all())
    # TODO scartare probes dello stesso device ricevute piu volte dallo stesso esp nello stesso minuto
    for probe in q2:
        probe.status = "pending"
        logger.info(probe)
    logger.info("------------------------------------")
    logger.info(str(db.session))
    db.session.commit()
    # logger.info(q2.all())
    # db.session.commit()

    # now_min = int(int(time.time()) / 60)
    # to_discard = db.session.query(Probe).filter(Probe.status == "unchecked").filter(now_min - Probe.timestamp > 2)

    # for probe in to_discard:
    #    probe.status = "discarded"

    # db.session.commit()
    # triangular_task.delay()
    logger.info("goodbye")
    return "done"


@celery.task(name="trilateration_task")
def trilateration_task():
    # to_do = db.session.query(Probe).filter(Probe.status == 'pending')

    return "triangular task"


def trilaterator(rssi_dict):
    data_dict = {
        device_id: (
            compute_distance(rssi),
            app.config["X" + device_id[-1:]],
            app.config["Y" + device_id[-1:]],
        )
        for device_id, rssi in rssi_dict.items()
    }
    data_list = list(data_dict.values())
    v_a = (
                  (data_list[2][1] ^ 2 - data_list[1][1] ^ 2)
                  + (data_list[2][2] ^ 2 - data_list[1][2] ^ 2)
                  + (data_list[1][0] ^ 2 - data_list[2][0] ^ 2)
          ) / 2

    v_b = (
                  (data_list[0][1] ^ 2 - data_list[1][1] ^ 2)
                  + (data_list[0][2] ^ 2 - data_list[1][2] ^ 2)
                  + (data_list[1][0] ^ 2 - data_list[0][1] ^ 2)
          ) / 2

    y = (
                v_b * (data_list[1][1] - data_list[2][1])
                - v_a * (data_list[1][1] - data_list[0][1])
        ) / (
                (data_list[0][2] - data_list[1][2]) * (data_list[1][1] - data_list[2][1])
                - (data_list[2][2] - data_list[1][2]) * (data_list[1][1] - data_list[2][1])
        )

    x = (y * (data_list[0][2] - data_list[1][2]) - v_b) / (
            data_list[1][1] - data_list[2][1]
    )

    return x, y


def compute_distance(rssi):
    distance = 10 ^ (
            (app.config["ESP_MES_POWER"] - rssi) / 10 * app.config["ENV_FACTOR"]
    )
    return distance
