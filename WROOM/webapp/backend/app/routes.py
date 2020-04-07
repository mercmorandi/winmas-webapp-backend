

from flask import current_app as app
from . import db_connection
from flask import request

@app.route('/', methods=['GET'])
def index():
    return 'hello world'

@app.route('/info', methods=['GET'])
def database_info():
    """
        Returns the all data stored in the database.
    """
    try:
        db = db_connection.DBConnection()
    except IOError:
        return "Database connection not possible", 504, {
            'ContentType': 'text/plain'
        }
    return db.get_database_info(), 200, {'ContentType': 'application/json'}

@app.route('/add_req', methods=['POST'])
def add_req():
    data = request.json
    print(data)
    return "ciao", 200, {
            'ContentType': 'text/plain'
        }