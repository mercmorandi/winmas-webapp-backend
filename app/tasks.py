from app import celery, db
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery.task
def add(a, b):
    return a + b


@celery.task(name="periodic_task")
def periodic_task():
    print('Hi! from periodic_task')
    logger.info("Hello! from periodic task")
    return 'ciao'
