from flask import current_app as app


def trilaterator(rssi_dict):
    data_dict = {
        esp_id: (
            compute_distance(rssi),
            int(app.config["X" + esp_id[-1:]]),
            int(app.config["Y" + esp_id[-1:]]),
        )
        for esp_id, rssi in rssi_dict.items()
    }

    print(str(data_dict))

    x_a = data_dict["EspWroom01"][1]
    x_b = data_dict["EspWroom02"][1]
    x_c = data_dict["EspWroom03"][1]
    y_a = data_dict["EspWroom01"][2]
    y_b = data_dict["EspWroom02"][2]
    y_c = data_dict["EspWroom03"][2]
    d_a = data_dict["EspWroom01"][0]
    d_b = data_dict["EspWroom02"][0]
    d_c = data_dict["EspWroom03"][0]

    v_a = ((x_c ** 2 - x_b ** 2) + (y_c ** 2 - y_b ** 2) + (d_b ** 2 - d_c ** 2)) / 2

    v_b = ((x_a ** 2 - x_b ** 2) + (y_a ** 2 - y_b ** 2) + (d_b ** 2 - d_a ** 2)) / 2

    y = (v_b * (x_b - x_c) - v_a * (x_b - x_a)) / (
        (y_a - y_b) * (x_b - x_c) - (y_c - y_b) * (x_b - x_c)
    )
    # fondamentale che y_a sia diverso da y_c

    x = (y * (y_a - y_b) - v_b) / (x_b - x_c)
    print("x: " + str(x) + " y: " + str(y))
    return x, y


def compute_distance(rssi):
    # distance = 10 ** (
    #        (int(app.config["ESP_MES_POWER"]) - rssi) / 10 * int(app.config["ENV_FACTOR"])
    # )
    a = int(app.config["ESP_MES_POWER"])
    n = int(app.config["ENV_FACTOR"])
    distance = 10 ** ((a - rssi) / (n * 10))
    return distance
