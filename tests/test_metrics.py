import logging
from unittest import mock

import pyairctrl

from py_air_control_exporter import app, metrics
from tests import status_responses


@mock.patch("pyairctrl.http_air_client.HTTPAirClient.get_status")
def test_metrics(mock_get_status, monkeypatch):
    """metrics endpoint produces the expected metrics"""
    mock_get_status.return_value = status_responses.SLEEP_STATUS
    monkeypatch.setenv(metrics.HOST_ENV_VAR, "127.0.0.1")
    response = app.create_app().test_client().get("/metrics")
    assert b"py_air_control_air_quality 1\n" in response.data
    assert b"py_air_control_is_manual 1\n" in response.data
    assert b"py_air_control_is_on 1\n" in response.data
    assert b"py_air_control_pm25 2\n" in response.data
    assert b"py_air_control_speed 0\n" in response.data


def test_metrics_no_host_provided(caplog):
    """error logs explain that the purifier host has to be provided through an env var"""
    caplog.set_level(logging.ERROR)
    response = app.create_app().test_client().get("/metrics")
    assert response.status_code == 500
    assert "Please specify the host address" in caplog.text
    assert metrics.HOST_ENV_VAR in caplog.text


@mock.patch("pyairctrl.http_air_client.HTTPAirClient.get_status")
def test_metrics_pyairctrl_failure(mock_get_status, monkeypatch, caplog):
    """error logs explain that there was a failure getting the status from pyairctrl"""
    mock_get_status.side_effect = Exception("Some foobar error")
    caplog.set_level(logging.ERROR)
    monkeypatch.setenv(metrics.HOST_ENV_VAR, "127.0.0.1")
    response = app.create_app().test_client().get("/metrics")
    assert response.status_code == 501
    assert "Could not read values from air control device" in caplog.text
    assert "Some foobar error" in caplog.text


def test_metrics_unknown_client(monkeypatch, caplog):
    """error logs explain that the chosen protocol is unknown"""
    monkeypatch.setenv(metrics.HOST_ENV_VAR, "127.0.0.1")
    monkeypatch.setenv(metrics.PROTOCOL_ENV_VAR, "foobar")
    response = app.create_app().test_client().get("/metrics")
    assert response.status_code == 500
    assert "Unknown protocol 'foobar'" in caplog.text


def test_get_client_http_protocol():
    assert isinstance(
        metrics.get_client("http", "1.2.3.4"), pyairctrl.http_air_client.HTTPAirClient
    )


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
