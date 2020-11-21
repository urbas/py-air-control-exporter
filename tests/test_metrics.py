import logging
from unittest import mock

import pytest

from py_air_control_exporter import app, metrics
from tests import status_responses


def test_metrics(mock_http_client, monkeypatch):
    """metrics endpoint produces the expected metrics"""
    monkeypatch.setenv(metrics.HOST_ENV_VAR, "127.0.0.1")
    response = app.create_app().test_client().get("/metrics")
    assert b"py_air_control_air_quality 1.0\n" in response.data
    assert b"py_air_control_is_manual 1.0\n" in response.data
    assert b"py_air_control_is_on 1.0\n" in response.data
    assert b"py_air_control_pm25 2.0\n" in response.data
    assert b"py_air_control_speed 0.0\n" in response.data
    assert b"IAI allergen index" in response.data


def test_metrics_fetched_again(mock_get_status, monkeypatch):
    """check that status is fetched every time metrics are pulled"""
    assert mock_get_status.call_count == 0
    test_client = app.create_app().test_client()
    assert mock_get_status.call_count == 1
    test_client.get("/metrics")
    assert mock_get_status.call_count == 2
    test_client.get("/metrics")
    assert mock_get_status.call_count == 3


def test_metrics_no_host_provided(caplog):
    """error logs explain that the purifier host has to be provided through an env var"""
    response = app.create_app().test_client().get("/metrics")
    assert not response.data
    assert "Please specify the host address" in caplog.text
    assert metrics.HOST_ENV_VAR in caplog.text


def test_metrics_pyairctrl_failure(mock_http_client, monkeypatch, caplog):
    """error logs explain that there was a failure getting the status from pyairctrl"""
    mock_http_client["get_status"].side_effect = Exception("Some foobar error")
    monkeypatch.setenv(metrics.HOST_ENV_VAR, "127.0.0.1")
    response = app.create_app().test_client().get("/metrics")
    assert not response.data
    assert "Could not read values from air control device" in caplog.text
    assert "Some foobar error" in caplog.text


def test_metrics_unknown_client(monkeypatch, caplog):
    """error logs explain that the chosen protocol is unknown"""
    monkeypatch.setenv(metrics.HOST_ENV_VAR, "127.0.0.1")
    monkeypatch.setenv(metrics.PROTOCOL_ENV_VAR, "foobar")
    response = app.create_app().test_client().get("/metrics")
    assert not response.data
    assert "Unknown protocol 'foobar'" in caplog.text


@mock.patch("pyairctrl.http_client.HTTPAirClient")
def test_get_client_http_protocol(mock_http_client):
    assert metrics.get_client("http", "1.2.3.4") == mock_http_client.return_value


@mock.patch("pyairctrl.coap_client.CoAPAirClient")
def test_get_client_coap_protocol(mock_coap_client):
    assert metrics.get_client("coap", "1.2.3.4") == mock_coap_client.return_value
    mock_coap_client.assert_called_with("1.2.3.4")


@mock.patch("pyairctrl.plain_coap_client.PlainCoAPAirClient")
def test_get_client_plain_coap_protocol(mock_plain_coap_client):
    assert (
        metrics.get_client("plain_coap", "1.2.3.4")
        == mock_plain_coap_client.return_value
    )
    mock_plain_coap_client.assert_called_with("1.2.3.4")


@pytest.fixture(autouse=1)
def _log_level_error(caplog):
    caplog.set_level(logging.ERROR)


@pytest.fixture(name="mock_get_status")
def _mock_get_status(caplog):
    with mock.patch("py_air_control_exporter.metrics.get_status") as mock_get_status:
        mock_get_status.return_value = status_responses.SLEEP_STATUS
        yield mock_get_status


@pytest.fixture(name="mock_http_client")
def _mock_http_client(caplog):
    with mock.patch(
        "pyairctrl.http_client.HTTPAirClient.__init__", return_value=None
    ), mock.patch("pyairctrl.http_client.HTTPAirClient.get_status") as mock_get_status:
        mock_get_status.return_value = status_responses.SLEEP_STATUS
        yield {"get_status": mock_get_status}
