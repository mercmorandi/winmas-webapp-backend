from collections import namedtuple
from flask import current_app as app

PosDTO = namedtuple("PosDTO", "name, x, y")


def toPosDTOdict(name, pos):
    return dict(PosDTO(name=name, x=pos["X"], y=pos["Y"])._asdict())


def serve_esp_pos():
    esp_dict = app.config["ESP_CONFIG"]["esp_list"]
    res = [toPosDTOdict(name, pos) for name, pos in esp_dict.items()]

    return res
