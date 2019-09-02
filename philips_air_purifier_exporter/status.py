_FAN_SPEED_TO_INT = {"s": 0, "1": 1, "2": 2, "3": 3, "t": 4}


def fan_speed_to_int(fan_speed):
    return _FAN_SPEED_TO_INT[fan_speed]


def is_on(status):
    return status["pwr"] == "1"
