from textwrap import dedent
from philips_air_purifier_exporter.prometheus import to_metrics
from test import status_responses


def test_to_metrics():
    assert (
        to_metrics(status_responses.SLEEP_STATUS)
        == dedent(
            """
        air_quality 1
        is_manual 1
        is_on 1
        pm25 2
        speed 0
    """
        ).lstrip()
    )
