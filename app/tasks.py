from app import celery, jobs, utils, proxy, socketio
from celery.utils.log import get_task_logger
from flask_socketio import send

logger = get_task_logger(__name__)


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


@celery.task(name="start_passive_socket")
def start_passive_socket(host, port):
    proxy.init_socket(host, port)


@celery.task(name="parse_proxy_data")
def parse_proxy_data(data):
    utils.proxy_data_parser(data)
