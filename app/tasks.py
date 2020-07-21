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


@celery.task(name="test_task1")
def test_task1(test):
    logger.info("Hello! from test task1: " + test)
    test_task2.delay("porcodio2")


@celery.task(name="test_task2")
def test_task2(test2):
    logger.info("Hello! from test task2: " + test2)


@celery.task(name="discardable_check_task")
def discardable_check_task():
    jobs.discardable_check_job()


@celery.task(name="trilateration_task")
def trilateration_task(p_hash):
    logger.info("trilateration task: " + p_hash)
    jobs.trilateration_job(p_hash)


@celery.task(name="trilaterable_check_task")
def trilaterable_check_task(p_hash):
    print("into check task")
    logger.info("trilateration check: " + p_hash)
    jobs.trilaterable_check_job(p_hash)
