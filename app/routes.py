from flask import current_app as app
from flask_cors import cross_origin

from . import db_connection
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

from app import db, tasks, statistic, positions, celery
from app.models import probes, locations, devices
from app.utils import date_parser


@app.route("/", methods=["GET"])
def index():
    # tasks.add.delay(11, 22)
    return "hello world"


# @app.route("/test_task", methods=["GET"])
# def test_task():
#    tasks.test_task1.delay("porcodio")
#    return "test task done", 200


@app.route("/add_req", methods=["POST"])
def add_req():
    if not request.json:
        return "no data", 400

    print(str(request.json))
    return probes.probe_parser(request.json)


@app.route("/stats", methods=["GET"])
@cross_origin()
def get_stats():
    if not request:
        return "error", 400

    start_date = request.args.get("start_date")

    return statistic.serve_stats(start_date), 200


@app.route("/get_esps", methods=["GET"])
@cross_origin()
def get_esps_new():
    if not request:
        return "error", 400
    res = positions.serve_esp_pos()
    return jsonify(res)


@app.route("/lastLocation", methods=["GET"])
@cross_origin()
def get_last_locations():
    if not request:
        return "error", 400
    start_date = date_parser(request.args.get("start_date"))
    end_date = date_parser(request.args.get("end_date"))
    res = locations.serve_last_locations(start_date, end_date)
    return jsonify(res)


@app.route("/activeLocation", methods=["GET"])
@cross_origin()
def get_active_locations():
    if not request:
        return "error", 400
    start_date = date_parser(request.args.get("start_date"))
    end_date = date_parser(request.args.get("end_date"))
    res = locations.serve_active_locations(start_date, end_date)
    return jsonify(res)


@app.route("/device/<int:device_id>")
@cross_origin()
def get_device(device_id):
    if not request:
        return "error", 400
    res = devices.serve_device_info(device_id)
    if res:
        return jsonify(res)
    else:
        return "resource not found", 404


@app.route("/start_proxy/", methods=["POST"])
@cross_origin()
def start_proxy():
    if not request:
        return "error", 400
    print(str(request.json))
    host = request.json["host"]
    port = request.json["port"]
    task = tasks.start_passive_socket.delay(host, port)
    app.config["ESP_CONFIG"]["proxy_task_id"] = task.id
    print(app.config["ESP_CONFIG"]["proxy_task_id"])
    return "ok", 200


@app.route("/stop_proxy/")
@cross_origin()
def stop_proxy():
    print("stopping proxy")
    print(app.config["ESP_CONFIG"]["proxy_task_id"])
    celery.control.revoke(app.config["ESP_CONFIG"]["proxy_task_id"], terminate= True)  # terminate= True
    app.config["ESP_CONFIG"]["proxy_task_id"] = None
    print("stopped proxy")
    print(app.config["ESP_CONFIG"]["proxy_task_id"])
    return "ok", 200
