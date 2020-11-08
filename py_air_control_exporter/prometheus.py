from textwrap import dedent

_FAN_SPEED_TO_INT = {"s": 0, "1": 1, "2": 2, "3": 3, "t": 4}


def to_metrics(status):
    return dedent(
        f"""
        py_air_control_air_quality {status["iaql"]}
        py_air_control_is_manual {1 if is_manual_mode(status) else 0}
        py_air_control_is_on {1 if is_on(status) else 0}
        py_air_control_pm25 {status["pm25"]}
        py_air_control_speed {fan_speed_to_int(status)}
    """
    ).lstrip()


def fan_speed_to_int(status):
    return _FAN_SPEED_TO_INT[status["om"]]


def is_on(status):
    return status["pwr"] == "1"


def is_manual_mode(status):
    return status["mode"] == "M"
