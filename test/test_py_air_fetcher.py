import logging
from test import status_responses
from unittest import mock

import pytest

from py_air_control_exporter import metrics, py_air_fetcher


def test_metrics_no_host_provided(caplog):
    """
    Error logs explain that the purifier host has to be provided through an env var
    """
    assert py_air_fetcher.get_reading() is None
    assert "Please specify the host address" in caplog.text
    assert py_air_fetcher.HOST_ENV_VAR in caplog.text


def test_metrics_pyairctrl_failure(mock_http_client, caplog):
    """Error logs explain that there was a failure getting the status from pyairctrl"""
    mock_http_client["get_status"].side_effect = Exception("Some foobar error")
    assert py_air_fetcher.get_reading(host="1.2.3.4", protocol="http") is None
    assert "Could not read values from air control device" in caplog.text
    assert "Some foobar error" in caplog.text


def test_metrics_unknown_client(caplog):
    """Error logs explain that the chosen protocol is unknown"""
    assert py_air_fetcher.get_reading(host="1.2.3.4", protocol="foobar") is None
    assert "Unknown protocol 'foobar'" in caplog.text


@mock.patch("pyairctrl.http_client.HTTPAirClient")
def test_get_client_http_protocol(mock_http_client):
    assert py_air_fetcher.get_client("http", "1.2.3.4") == mock_http_client.return_value


@mock.patch("pyairctrl.coap_client.CoAPAirClient")
def test_get_client_coap_protocol(mock_coap_client):
    assert py_air_fetcher.get_client("coap", "1.2.3.4") == mock_coap_client.return_value
    mock_coap_client.assert_called_with("1.2.3.4")


@mock.patch("pyairctrl.plain_coap_client.PlainCoAPAirClient")
def test_get_client_plain_coap_protocol(mock_plain_coap_client):
    assert (
        py_air_fetcher.get_client("plain_coap", "1.2.3.4")
        == mock_plain_coap_client.return_value
    )
    mock_plain_coap_client.assert_called_with("1.2.3.4")


@pytest.mark.usefixtures("mock_http_client")
def test_get_reading():
    assert py_air_fetcher.get_reading("1.2.3.4", "http") == metrics.TargetReading(
        status=metrics.Status(fan_speed=0, iaql=1, is_manual=True, is_on=True, pm25=2),
        filters={
            "0": metrics.Filter(hours=0, filter_type=""),
            "1": metrics.Filter(hours=185, filter_type="A3"),
            "2": metrics.Filter(hours=2228, filter_type="C7"),
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
