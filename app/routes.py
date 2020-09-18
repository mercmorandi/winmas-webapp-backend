from flask import current_app as app
from flask_cors import cross_origin

from flask import request, jsonify

from app import tasks, statistic, positions, celery, socketio, proxy
from app.models import probes, locations, devices
from app.utils import date_parser


@app.route("/", methods=["GET"])
def index():
    return "hello world"


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


@app.route("/proxy_port/", methods=["GET"])
@cross_origin()
def get_proxy_port():
    if not request:
        return "error", 400

    return app.config["PROXY_PORT"], 200


@app.route("/start_proxy/", methods=["GET"])
@cross_origin()
def start_proxy():
    if not request:
        return "error", 400
    if app.config["ESP_CONFIG"]["proxy_task_id"] != "None":
        return "proxy already up", 200

    host = app.config["PROXY_UID"]
    port = app.config["PROXY_PORT"]
    task = tasks.start_passive_socket.delay(host, port)
    socketio.emit("proxy_status", "starting")
    app.config["ESP_CONFIG"]["proxy_task_id"] = task.id
    return jsonify("ok"), 200


@app.route("/stop_proxy/", methods=["GET"])
@cross_origin()
def stop_proxy():
    if not request:
        return "error", 400
    if app.config["ESP_CONFIG"]["proxy_task_id"] == "None":
        return "proxy already down", 200

    socketio.emit("proxy_status", "stopping")
    proxy.close_proxy_server(app.config["PROXY_UID"], int(app.config["PROXY_PORT"]))
    app.config["ESP_CONFIG"]["proxy_task_id"] = "None"
    return "ok", 200


@app.route("/current_proxy_status/", methods=["GET"])
@cross_origin()
def get_proxy_status():
    if not request:
        return "error", 400
    print(app.config["ESP_CONFIG"]["proxy_task_id"])
    res = {}
    if app.config["ESP_CONFIG"]["proxy_task_id"] == "None":
        res["status"] = "off"
    else:
        res["status"] = "on"

    return jsonify(res)


@app.route("/proxy_status", methods=["POST"])
@cross_origin()
def set_proxy_status():
    if not request:
        return "error", 400

    # edge case
    status = request.json.get("status")
    if status == "on" and app.config["ESP_CONFIG"]["proxy_task_id"] == "None":
        app.config["ESP_CONFIG"]["proxy_task_id"] = request.json.get("task_id")

    print("proxy status: " + str(status))
    socketio.emit("proxy_status", status)
    return "ok", 200


@app.route("/new_location_event", methods=["POST"])
@cross_origin()
def notify_new_location():
    if not request:
        return "error", 400

    res = request.json
    socketio.emit("new-location", res)
    return "ok", 200
