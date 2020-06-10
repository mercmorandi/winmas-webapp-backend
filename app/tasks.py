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


@celery.task(name="triangular_task")
def triangular_task():
    # to_do = db.session.query(Probe).filter(Probe.status == 'pending')
    return "triangular task"
