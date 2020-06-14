from app import celery
from app import create_app
from app.celery_utils import init_celery

# celery worker -A celery_worker.celery --loglevel=info

app = create_app()
init_celery(celery, app)
