import os
from dotenv import load_dotenv

#env var are into a .env file ih this folder (create it if not exists )
load_dotenv()

#https://exploreflask.com/en/latest/configuration.html
class Config(object):
    DEBUG = os.getenv("FLASK_DEBUG")
    DEVELOPMENT=os.getenv("DEVELOPMENT")
    FLASK_DEBUG=os.getenv("FLASK_DEBUG")
    FLASK_ENV=os.getenv("FLASK_ENV")
    POSTGRES_USER=os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB=os.getenv("POSTGRES_DB")
   