import requests
import random
import time
import os

import click

from urllib.parse import urljoin

data_seed = {
    "data": [
        {
            "timestamp": "565",
            "destination": "ff:ff:ff:ff:ff:ff",
            "source": "00:19:88:15:6d:5e",
            "bssid": "ff:ff:ff:ff:ff:ff",
            "ssid": "pib1",
            "signal_strength_wroom": "-88",
            "signal_strength_rt": "109",
        },
        {
            "timestamp": "2115",
            "destination": "ff:ff:ff:ff:ff:ff",
            "source": "00:20:4a:b3:5b:7c",
            "bssid": "ff:ff:ff:ff:ff:ff",
            "ssid": "next",
            "signal_strength_wroom": "-80",
            "signal_strength_rt": "91",
        },
        {
            "timestamp": "3935",
            "destination": "ff:ff:ff:ff:ff:ff",
            "source": "8e:b0:9f:69:d7:b6",
            "bssid": "ff:ff:ff:ff:ff:ff",
            "ssid": "None",
            "signal_strength_wroom": "-88",
            "signal_strength_rt": "-41",
        },
    ],
    "device_id": "EspWroom01",
    "captured_device": 3,
}


def random_generator(data, device_id):
    out = {}
    out["captured_device"] = data["captured_device"]
    out["device_id"] = device_id
    out["data"] = []

    for probe in data["data"]:
        temp_prob = probe
        temp_prob["signal_strength_wroom"] = str(
            int(temp_prob["signal_strength_wroom"]) + random.randint(1, 30)
        )
        temp_prob["signal_strength_rt"] = str(
            int(temp_prob["signal_strength_wroom"]) + random.randint(1, 30)
        )
        out["data"].append(temp_prob)

    return out


def devices_ids(n_devices):
    device_id = 1
    while n_devices:
        yield f"EspWroom0{device_id}"
        device_id += 1
        n_devices -= 1


@click.command()
@click.option("--n_devices", default=3, help="Number of devices sending data.")
@click.option(
    "--minutes",
    default=None,
    help="Number minutes to stay alive. Default value does not stop.",
)
def send_data(n_devices, minutes):
    """ESP Client mocker.
    Sends requests to flask with probe data
    """
    base_url = os.getenv("FLASK_URL", "http://localhost:5000/")
    endless = True if minutes is None else False
    while endless or minutes:
        for device_id in devices_ids(n_devices):
            data = random_generator(data_seed, device_id)
            requests.post(urljoin(base_url, "add_req"), json=data)
            time.sleep(1)
        time.sleep(60)
        if minutes:
            minutes -= 1


if __name__ == "__main__":
    send_data()
