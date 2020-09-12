from app import celery, jobs, utils, proxy, socketio
from celery.utils.log import get_task_logger
from flask_socketio import send

logger = get_task_logger(__name__)


# @celery.task(name="periodic_task")
# def periodic_task():
#     print("Hi! from periodic_task")
#     logger.info("Hello! from periodic task")
#     return "ciao"


# @celery.task(name="test_task1")
# def test_task1(test):
#    logger.info("Hello! from test task1: " + test)
#    test_task2.delay("porcodio2")


@socketio.on("proxy_status")
def notify_proxy_status(status):
    print("into notify")
    send(status)


@celery.task(name="test_task", bind=True)
def test_task(self):
    # socketio.emit("proxy_status", "ciaooooooooooo")
    self.update_state(state="PROGRESS", meta={"host": "suca", "port": "coglione"})
    # notify_proxy_status("porco il clero")


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
