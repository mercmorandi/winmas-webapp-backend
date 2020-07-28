import time

from flask import current_app as app
from flask_cors import cross_origin

from . import db_connection
from flask import request
from sqlalchemy.exc import IntegrityError

from app import db, tasks, statistic, positions
from app.models import probes


@app.route("/", methods=["GET"])
def index():
    tasks.add.delay(11, 22)
    return "hello world"


@app.route("/info", methods=["GET"])
def database_info():
    """
        Returns the all data stored in the database.
    """
    try:
        db = db_connection.DBConnection()
    except IOError:
        return "Database connection not possible", 504, {"ContentType": "text/plain"}
    return db.get_database_info(), 200, {"ContentType": "application/json"}


@app.route("/test_task", methods=["GET"])
def test_task():
    tasks.test_task1.delay("porcodio")
    return "test task done", 200


@app.route("/add_req_test", methods=["POST"])
def add_req_test():
    if not request.json:
        return "no data", 400

    print(str(request.json))
    req = request.json
    device_id = req["device_id"]
    on_since = int(req["on_since"])
    probe = req["probe"]

    ts = int(round(time.time() * 1000)) - (on_since - int(probe["timestamp"]))
    minutes_ts = int(ts / 1000 / 60)
    to_encode = (
            probe["destination"]
            + ""
            + probe["source"]
            + ""
            + str(minutes_ts)
            + ""
            + probe["seq_number"]
    )
    h = md5(to_encode.encode("utf-8")).hexdigest()
    print("HASSSSSSSSH: " + str(h))
    return "ok", 200


@app.route("/add_req", methods=["POST"])
def add_req():
    if not request.json:
        return "no data", 400

    print(str(request.json))
    probe = probes.probe_parser(request.json)

    db.session.add(probe)
    try:
        db.session.commit()
        db.session.close()
        tasks.trilaterable_check_task.delay(str(probe.hash))
        return "ok", 200
    except IntegrityError:
        db.session.rollback()
        return (
            "hash: " + str(probe.hash) + " and esp_id: " + probe.esp_id + " already exists",
            409,
        )
        # error, there already is a probe using this hash and esp_id
        # constraint failed


@app.route("/stats", methods=["GET"])
@cross_origin()
def get_stats():
    if not request:
        return "error", 400

    start_date = request.args.get("start_date")

    return statistic.serve_stats(start_date), 200


# TODO: manage possible errors
@app.route("/get_esps", methods=["GET"])
@cross_origin()
def get_esps():
    return positions.PosDto().get_esps(), 200


@app.route("/lastPosition", methods=["GET"])
@cross_origin()
def get_last_positions():
    if not request:
        return "error", 400
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")


@app.route("/activePosition", methods=["GET"])
@cross_origin()
def get_active_positions():
    if not request:
        return "error", 400
