from app import celery, jobs
from celery.utils.log import get_task_logger


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
    jobs.filter_job()
    logger.info("filter job done")


@celery.task(name="trilateration_task")
def trilateration_task():
    jobs.trilateration_job()
    logger.info("trilateration done")
