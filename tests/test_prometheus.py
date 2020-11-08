from textwrap import dedent

from py_air_control_exporter.prometheus import to_metrics
from tests import status_responses


def test_to_metrics():
    assert (
        to_metrics(status_responses.SLEEP_STATUS)
        == dedent(
            """
        py_air_control_air_quality 1
        py_air_control_is_manual 1
        py_air_control_is_on 1
        py_air_control_pm25 2
        py_air_control_speed 0
    """
        ).lstrip()
    )
