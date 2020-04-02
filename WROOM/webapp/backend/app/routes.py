

from flask import current_app as app
from . import db_connection

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