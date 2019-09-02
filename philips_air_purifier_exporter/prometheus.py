from textwrap import dedent
from philips_air_purifier_exporter.status import is_manual_mode, is_on, fan_speed_to_int


def to_metrics(status):
    return dedent(
        """
        air_quality {air_quality}
        is_manual {is_manual}
        is_on {is_on}
        pm25 {pm25}
        speed {speed}
    """.format(
            air_quality=status["iaql"],
            is_manual=1 if is_manual_mode(status) else 0,
            is_on=1 if is_on(status) else 0,
            pm25=status["pm25"],
            speed=fan_speed_to_int(status),
        )
    ).lstrip()
