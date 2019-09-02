_FAN_SPEED_TO_INT = {"s": 0, "1": 1, "2": 2, "3": 3, "t": 4}


def fan_speed_to_int(status):
    return _FAN_SPEED_TO_INT[status["om"]]


def is_on(status):
    return status["pwr"] == "1"


def is_manual_mode(status):
    return status["mode"] == "M"
