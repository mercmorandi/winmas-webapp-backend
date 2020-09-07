import time
from datetime import datetime
from hashlib import md5

from app.models import probes


def date_parser(date):
    return datetime.fromtimestamp(int(date)).replace(second=0, microsecond=0)


def esp_ts_minutes_seconds(esp_ts, on_since):
    ts = int(round(time.time() * 1000)) - (on_since - int(esp_ts))
    return int(ts / 1000 / 60), int(ts / 1000)


def md5_encoder(*args):
    to_encode = [param for param in args]
    return md5("".join(to_encode).encode("utf-8")).hexdigest()


def proxy_data_parser(data):
    req = {}
    s = data.split('\n', 1)[1]

    req['data'] = []
    req['device_id'] = data.split(',', 1)[0]
    req['on_since'] = data.split(',', 2)[2].split('\n', 1)[0]
    cont = req['captured_device'] = int(data.split(',', 2)[1])

    get_next_req(req, s, cont)

    print(req['device_id'] + " ----> all proxied to flask")
    # r = requests.post('http://localhost:5000/add_req',json = req)
    # print('proxied to flask: '+str(r))


def get_next_req(req, s, cont):
    splitted = s.split('\n', 1)

    if cont == 0:
        return

    add_req(req, splitted[0])
    cont -= 1
    get_next_req(req, splitted[1], cont)


def add_req(req, packet):
    values = packet.split(',', 7)
    s = {'timestamp': values[0], 'destination': values[1], 'source': values[2], 'bssid': values[3], 'ssid': values[4],
         'seq_number': values[5], 'signal_strength_wroom': values[6], 'signal_strength_rt': values[7]}

    req['data'].append(s)
    pp = {'probe': s, 'on_since': req['on_since'], 'captured_device': req['captured_device'],
          'device_id': req['device_id']}
    # r = requests.post('http://localhost:5000/add_req',json = pp)
    probes.probe_parser(pp)
    #print('req parsed: '+str(pp))