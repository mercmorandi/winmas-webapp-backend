import time

from flask import current_app as app
from . import db_connection
from flask import request

from .models import probes

from hashlib import md5

from app import db
from . import tasks


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


@app.route("/add_req", methods=["POST"])
def add_req():
    if not request.json:
        return "no data", 400

    print(str(request.json))
    req = request.json
    device_id = req["device_id"]
    # captured_device = req['captured_device']
    data = req["data"]
    on_since = int(req["on_since"])
    for probe in data:
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
        probe = probes.Probe(
            destination=probe["destination"],
            source=probe["source"],
            bssid=probe["bssid"],
            ssid=probe["ssid"],
            signal_strength_wroom=probe["signal_strength_wroom"],
            signal_strength_rt=probe["signal_strength_rt"],
            hash=str(h),
            timestamp=ts,
            device_id=device_id,
            status="unchecked",
        )

        db.session.add(probe)
        db.session.commit()

    return "ok", 200


# esp_data, devices_id = [], []
# global esp_data
# global devices_id
#
# if data["device_id"] not in devices_id:
#    devices_id.append(data["device_id"])
#    esp_data.append(data)
#
#    if len(esp_data) is app.config["NUMESP"]:
#        print("%d packets found" % (app.config["NUMESP"]))
#        v = get_valid_packets(esp_data)
#        print("Cleaning up variables")
#        esp_data, devices_id = [], []
#        print(v)


# def get_valid_packets(data):
#    valid_packets = []
#
#    for datum in data[0]["data"]:
#
#        valid_packet = {}
#        valid_packet["MAC"] = datum["source"]
#        valid_packet["SSID"] = datum["ssid"]
#        valid_packet["time"] = datum["timestamp"]
#        valid_packet["signals"] = []
#
#        valid_packet["signals"].append(
#            {data[0]["device_id"]: datum["signal_strength_wroom"]}
#        )
#
#        cont = 1
#
#        timestamp = datum["timestamp"]
#        MAC = datum["source"]
#
#        for esp in data[1:]:
#            packet = [
#                p
#                for p in esp["data"]
#                if p["timestamp"] is timestamp and p["source"] is MAC
#            ][0]
#
#            if not packet:
#                break
#
#            valid_packet["signals"].append(
#                {esp["device_id"]: packet["signal_strength_wroom"]}
#            )
#            cont += 1
#            if cont is len(data):
#                valid_packets.append(valid_packet)
#
#    return valid_packets
