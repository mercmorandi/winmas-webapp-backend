from flask import current_app as app
from . import db_connection
from flask import request


@app.route("/", methods=["GET"])
def index():
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


esp_data, devices_id = [], []


@app.route("/add_req", methods=["POST"])
def add_req():
    data = request.json

    global esp_data
    global devices_id

    if data["device_id"] not in devices_id:
        devices_id.append(data["device_id"])
        esp_data.append(data)

        if len(esp_data) is app.config["NUMESP"]:
            print("%d packets found" % (app.config["NUMESP"]))
            v = get_valid_packets(esp_data)
            print("Cleaning up variables")
            esp_data, devices_id = [], []
            print(v)


def get_valid_packets(data):
    valid_packets = []

    for datum in data[0]["data"]:

        valid_packet = {}
        valid_packet["MAC"] = datum["source"]
        valid_packet["SSID"] = datum["ssid"]
        valid_packet["time"] = datum["timestamp"]
        valid_packet["signals"] = []

        valid_packet["signals"].append(
            {data[0]["device_id"]: datum["signal_strength_wroom"]}
        )

        cont = 1

        timestamp = datum["timestamp"]
        MAC = datum["source"]

        for esp in data[1:]:
            packet = [
                p
                for p in esp["data"]
                if p["timestamp"] is timestamp and p["source"] is MAC
            ][0]

            if not packet:
                break

            valid_packet["signals"].append(
                {esp["device_id"]: packet["signal_strength_wroom"]}
            )
            cont += 1
            if cont is len(data):
                valid_packets.append(valid_packet)

    return valid_packets
