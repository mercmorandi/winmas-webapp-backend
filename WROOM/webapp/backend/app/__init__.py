import os

from flask import Flask

#https://github.com/mukul-rathi/CleanCycle/blob/tutorial/src/db_connection.py
from . import db_connection

def init_db():
    
    print("Beginning init db procedure...")  #for debugging
    db = db_connection.DBConnection()  
    print("Established connection to db...")  #for debugging
    db.create_tables()
    print("Created database tables")  #for debugging
    #clear any lingering data and start afresh
    db.clear_data()

init_db()

app = Flask(__name__) 

with app.app_context():
        # Imports
    from . import routes




