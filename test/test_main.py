from unittest import mock

import pytest
from click.testing import CliRunner

from py_air_control_exporter import app, main


def test_help():
    result = CliRunner().invoke(main.main, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_main(mock_app, mock_create_targets):
    """Check that the exporter Flask app is created with all the given parameters"""
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
    mock_create_targets.assert_called_once_with(
        {"192.168.1.123": {"host": "192.168.1.123", "protocol": "coap"}}
    )
    expected_targets = mock_create_targets.return_value
    app.create_app.assert_called_once_with(expected_targets)
    mock_app.run.assert_called_once_with(host="1.2.3.4", port=12345)


def test_unknown_protocol():
    """Check that failure is reporter if an invalid protocol is provided"""
    result = CliRunner(mix_stderr=False).invoke(
        main.main,
        ["--host", "192.168.1.123", "--protocol", "foobar"],
    )
    assert result.exit_code != 0
    assert "--protocol" in result.stderr


@pytest.mark.usefixtures("mock_app")
def test_config_file(mock_create_targets):
    """Check that the exporter Flask app is created with config file parameters"""
    result = CliRunner().invoke(
        main.main,
        [
            "--config",
            "test/data/simple_config.yaml",
            "--listen-address",
            "1.2.3.4",
            "--listen-port",
            "12345",
        ],
    )
    assert result.exit_code == 0
    mock_create_targets.assert_called_once_with(
        {
            "foo": {"host": "1.2.3.4", "protocol": "coap"},
            "bar": {"host": "1.2.3.5", "protocol": "http"},
        }
    )


def test_default_parameters(mock_app, mock_create_targets):
    """Check that the exporter Flask app is created with the given hostname and default
    parameters
    """
    result = CliRunner().invoke(main.main, ["--host", "192.168.1.123"])
    assert result.exit_code == 0
    mock_create_targets.assert_called_once_with(
        {"192.168.1.123": {"host": "192.168.1.123", "protocol": "http"}}
    )
    mock_app.run.assert_called_once_with(host="127.0.0.1", port=9896)


def test_create_targets(mocker):
    """Check that the targets dictionary is created and ready to fetch."""
    mock_get_reading = mocker.patch(
        "py_air_control_exporter.py_air_fetcher.get_reading",
        autospec=True,
    )

    targets_config = {
        "foo": {"host": "1.2.3.4", "protocol": "coap"},
        "bar": {"host": "1.2.3.5", "protocol": "http"},
    }
    targets = main.create_targets(targets_config)
    assert isinstance(targets, dict)
    assert len(targets) == 2
    assert "foo" in targets
    assert "bar" in targets

    # Call first fetcher and verify arguments
    targets["foo"].fetcher()
    mock_get_reading.assert_called_with("1.2.3.4", "coap")

    # Call second fetcher and verify arguments
    targets["bar"].fetcher()
    mock_get_reading.assert_called_with("1.2.3.5", "http")


@pytest.fixture(name="mock_app")
def _mock_app(mocker):
    return mocker.patch(
        "py_air_control_exporter.app.create_app",
        return_value=mock.Mock(),
    ).return_value


@pytest.fixture(name="mock_create_targets")
def _mock_create_targets(mocker):
    return mocker.patch(
        "py_air_control_exporter.main.create_targets",
        autospec=True,
    )
