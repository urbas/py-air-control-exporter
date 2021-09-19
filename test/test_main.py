import sys
from unittest import mock

import pytest

from py_air_control_exporter import app
from py_air_control_exporter.main import main


def test_help(monkeypatch, capfd):
    monkeypatch.setattr(sys, "argv", ["app-name", "--help"])
    with pytest.raises(SystemExit) as ex_info:
        main()
    assert ex_info.value.code == 0
    assert "Usage" in capfd.readouterr().out


def test_main(mock_app, monkeypatch):
    """check that the exporter Flask app is created with all the given parameters"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "app-name",
            "--host",
            "192.168.1.123",
            "--protocol",
            "coap",
            "--listen-address",
            "1.2.3.4",
            "--listen-port",
            "12345",
        ],
    )
    with pytest.raises(SystemExit) as ex_info:
        main()
    assert ex_info.value.code == 0
    app.create_app.assert_called_once_with(host="192.168.1.123", protocol="coap")
    mock_app.run.assert_called_once_with(host="1.2.3.4", port=12345)


def test_hostname_required(monkeypatch, capfd):
    """check that the hostname of the purifier is a required option"""
    monkeypatch.setattr(sys, "argv", ["app-name"])
    with pytest.raises(SystemExit) as ex_info:
        main()
    assert ex_info.value.code != 0
    assert "--host" in capfd.readouterr().err


def test_unknown_protocol(monkeypatch, capfd):
    """check that failure is reporter if an invalid protocol is provided"""
    monkeypatch.setattr(
        sys, "argv", ["app-name", "--host", "192.168.1.123", "--protocol", "foobar"]
    )
    with pytest.raises(SystemExit) as ex_info:
        main()
    assert ex_info.value.code != 0
    assert "--protocol" in capfd.readouterr().err


def test_default_parameters(mock_app, monkeypatch):
    """
    check that the exporter Flask app is created with the given hostname and default
    parameters
    """
    monkeypatch.setattr(sys, "argv", ["app-name", "--host", "192.168.1.123"])
    with pytest.raises(SystemExit) as ex_info:
        main()
    assert ex_info.value.code == 0
    app.create_app.assert_called_once_with(host="192.168.1.123", protocol="http")
    mock_app.run.assert_called_once_with(host="0.0.0.0", port=9896)


@pytest.fixture(name="mock_app")
def _mock_app():
    with mock.patch("py_air_control_exporter.app.create_app") as mock_create_app:
        mock_create_app.return_value = mock.Mock()
        yield mock_create_app.return_value
