## Welcome to winmas flask backend

**To run server without docker**
    
1. Create a virtual environment with

    ``Python3 -m venv venv``

2. Activate your venv

    ``source venv/bin/activate``

3. Install dependencies

    ``pip install -r requirements.txt`` 

4. Export app name

    ``cd project``

    ``export FLASK_APP=app``

4. Run server

    ``flask run``
    
5. install Celery and rabbitMQ

6. Run celery worker

    ``celery worker -A celery_worker.celery --loglevel=info``
 
**To run dockerized app**

1. ``docker-compose build``

2. ``docker-compose up``

**Links**

Flask: https://flask.palletsprojects.com/en/1.1.x/tutorial/

RabbitMQ: https://www.rabbitmq.com/

Celery: https://docs.celeryproject.org/en/stable/getting-started/introduction.html

Postrges: https://www.postgresql.org/

PostgresSetup: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04
