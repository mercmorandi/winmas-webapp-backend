from app import celery
from app import create_app
from app.celery_utils import init_celery

# celery worker -A celery_worker.celery --loglevel=info   to start celery workers
# celery -A celery_worker.celery status --> to get the list of workers
# celery -A celery_worker.celery inspect active   --> to see what the workers are currently doing

app = create_app()
init_celery(celery, app)
