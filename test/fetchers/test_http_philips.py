import logging

import pytest

from py_air_control_exporter import fetchers_api
from py_air_control_exporter.fetchers import http_philips
from test import status_responses


def test_metrics_pyairctrl_failure(mock_http_client, caplog):
    """Error logs explain that there was a failure getting the status from pyairctrl"""
    caplog.set_level(logging.ERROR)
    mock_http_client["get_status"].side_effect = Exception("Some foobar error")
    assert http_philips.get_reading(host="1.2.3.4") is None
    assert "Could not read values from air control device" in caplog.text
    assert "Some foobar error" in caplog.text


@pytest.mark.usefixtures("mock_http_client")
def test_get_reading():
    assert http_philips.get_reading("1.2.3.4") == fetchers_api.TargetReading(
        air_quality=fetchers_api.AirQuality(iaql=1, pm25=2),
        control_info=fetchers_api.ControlInfo(fan_speed=0, is_manual=True, is_on=True),
        filters={
            "0": fetchers_api.Filter(hours=0, filter_type=""),
            "1": fetchers_api.Filter(hours=185, filter_type="A3"),
            "2": fetchers_api.Filter(hours=2228, filter_type="C7"),
        },
    )


@pytest.fixture(autouse=True)
def _log_level_error(caplog):
    caplog.set_level(logging.ERROR)


@pytest.fixture(name="mock_http_client")
def _mock_http_client(mocker):
    mocker.patch("pyairctrl.http_client.HTTPAirClient.__init__", return_value=None)
    return {
        "get_status": mocker.patch(
            "pyairctrl.http_client.HTTPAirClient.get_status",
            return_value=status_responses.SLEEP_STATUS,
        ),
        "get_filters": mocker.patch(
            "pyairctrl.http_client.HTTPAirClient.get_filters",
            return_value=status_responses.FILTERS,
        ),
    }
