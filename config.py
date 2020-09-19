import os
from dotenv import load_dotenv


# env var are into a .env file ih this folder (create it if not exists )
load_dotenv()


# https://exploreflask.com/en/latest/configuration.html
class Config(object):
    DEBUG = os.getenv("FLASK_DEBUG")
    DEVELOPMENT = os.getenv("DEVELOPMENT")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG")
    FLASK_ENV = os.getenv("FLASK_ENV")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    NUMESP = os.getenv("N_ESP")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    ESP_MES_POWER = os.getenv("ESP_MES_POWER")
    ENV_FACTOR = os.getenv("ENV_FACTOR")
    X1 = os.getenv("X1")
    Y1 = os.getenv("Y1")
    X2 = os.getenv("X2")
    Y2 = os.getenv("Y2")
    X3 = os.getenv("X3")
    Y3 = os.getenv("Y3")
    PROXY_PORT = os.getenv("PROXY_PORT")
    CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL")
    PROXY_UID = os.getenv("PROXY_UID")
