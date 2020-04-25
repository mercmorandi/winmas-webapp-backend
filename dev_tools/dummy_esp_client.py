import requests
import random
import time

data_seed = {
        "data":[
            {
                "timestamp":"565",
                "destination":"ff:ff:ff:ff:ff:ff",
                "source":"00:19:88:15:6d:5e",
                "bssid":"ff:ff:ff:ff:ff:ff",
                "ssid":"pib1",
                "signal_strength_wroom":"-88",
                "signal_strength_rt":"109"
            },
            {
                "timestamp":"2115",
                "destination":"ff:ff:ff:ff:ff:ff",
                "source":"00:20:4a:b3:5b:7c",
                "bssid":"ff:ff:ff:ff:ff:ff",
                "ssid":"next",
                "signal_strength_wroom":"-80",
                "signal_strength_rt":"91"
            },
            {
                "timestamp":"3935",
                "destination":"ff:ff:ff:ff:ff:ff",
                "source":"8e:b0:9f:69:d7:b6",
                "bssid":"ff:ff:ff:ff:ff:ff",
                "ssid":"None",
                "signal_strength_wroom":"-88",
                "signal_strength_rt":"-41"
            }
        ],

    "device_id":"EspWroom01",
    "captured_device":3
}

def random_generator(data, device_id):
    out = {}
    out['captured_device'] = data['captured_device']
    out['device_id'] = 'EspWroom0'+str(device_id)
    out['data'] = []

    for probe in data['data']:
        temp_prob = probe
        temp_prob["signal_strength_wroom"] = str(int(temp_prob["signal_strength_wroom"]) + random.randint(1,30))
        temp_prob['signal_strength_rt'] = str(int(temp_prob["signal_strength_wroom"]) + random.randint(1,30))
        out['data'].append(temp_prob) 

    return out




while(True):

    for i in range(1,4):
        data = random_generator(data_seed, i)
        requests.post('http://localhost:5000/add_req', json=data)
        time.sleep(1)

    time.sleep(60)






