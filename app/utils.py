import time
from datetime import datetime
from hashlib import md5


def date_parser(date):
    return datetime.fromtimestamp(int(date)).replace(second=0, microsecond=0)


def esp_ts_minutes_seconds(esp_ts, on_since):
    ts = int(round(time.time() * 1000)) - (on_since - int(esp_ts))
    return int(ts / 1000 / 60), int(ts / 1000)


def md5_encoder(*args):
    to_encode = [param for param in args]
    return md5("".join(to_encode).encode("utf-8")).hexdigest()
