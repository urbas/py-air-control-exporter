from unittest import mock

import pytest
from click.testing import CliRunner

from py_air_control_exporter import app, main


def test_help(monkeypatch, capfd):
    result = CliRunner().invoke(main.main, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_main(mock_app, mock_create_status_fetcher):
    """check that the exporter Flask app is created with all the given parameters"""
    result = CliRunner().invoke(
        main.main,
        [
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
    assert result.exit_code == 0
    mock_create_status_fetcher.assert_called_once_with("192.168.1.123", "coap")
    app.create_app.assert_called_once_with(mock_create_status_fetcher.return_value)
    mock_app.run.assert_called_once_with(host="1.2.3.4", port=12345)


def test_hostname_required(monkeypatch, capfd):
    """check that the hostname of the purifier is a required option"""
    result = CliRunner(mix_stderr=False).invoke(main.main, [])
    assert result.exit_code != 0
    assert "--host" in result.stderr


def test_unknown_protocol(monkeypatch, capfd):
    """check that failure is reporter if an invalid protocol is provided"""
    result = CliRunner(mix_stderr=False).invoke(
        main.main, ["--host", "192.168.1.123", "--protocol", "foobar"]
    )
    assert result.exit_code != 0
    assert "--protocol" in result.stderr


def test_default_parameters(mock_app, mock_create_status_fetcher):
    """
    check that the exporter Flask app is created with the given hostname and default
    parameters
    """
    result = CliRunner().invoke(main.main, ["--host", "192.168.1.123"])
    assert result.exit_code == 0
    mock_create_status_fetcher.assert_called_once_with("192.168.1.123", "http")
    mock_app.run.assert_called_once_with(host="0.0.0.0", port=9896)


def test_create_status_fetcher(mocker, mock_app):
    """Check that the fetcher is created and is ready to fetch."""
    mock_get_status = mocker.patch(
        "py_air_control_exporter.py_air_fetcher.get_status", autospec=True
    )
    fetcher = main.create_status_fetcher("1.2.3.4")
    assert fetcher() == mock_get_status.return_value


@pytest.fixture(name="mock_app")
def _mock_app(mocker):
    yield mocker.patch(
        "py_air_control_exporter.app.create_app", return_value=mock.Mock()
    ).return_value


@pytest.fixture(name="mock_create_status_fetcher")
def _mock_create_status_fetcher(mocker):
    yield mocker.patch(
        "py_air_control_exporter.main.create_status_fetcher",
        autospec=True,
    )
