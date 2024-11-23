from collections.abc import Iterable
from unittest import mock

import pytest
from flask.testing import FlaskClient
from prometheus_client import Metric
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample

from py_air_control_exporter import fetchers_api, readings_source

SOME_READINGS = {
    "broken": fetchers_api.TargetReading(host="1.2.3.1", has_errors=True),
    "empty": fetchers_api.TargetReading(host="1.2.3.2"),
    "full": fetchers_api.TargetReading(
        host="1.2.3.4",
        air_quality=fetchers_api.AirQuality(iaql=3, pm25=5),
        control_info=fetchers_api.ControlInfo(fan_speed=2, is_manual=True, is_on=True),
        filters={
            "0": fetchers_api.Filter(hours=42, filter_type=""),
            "1": fetchers_api.Filter(hours=185, filter_type="A3"),
            "2": fetchers_api.Filter(hours=9001, filter_type="C7"),
        },
    ),
}


def get_samples(client: FlaskClient) -> list[Sample]:
    actual_metrics = _response_to_metrics(client.get("/metrics"))
    return [sample for metric in actual_metrics for sample in metric.samples]


def _response_to_metrics(response) -> Iterable[Metric]:
    return text_string_to_metric_families(response.data.decode("utf-8"))


@pytest.fixture(name="mock_readings_source")
def _mock_readings_source():
    return mock.Mock(spec=readings_source.ReadingsSource, return_value=SOME_READINGS)
