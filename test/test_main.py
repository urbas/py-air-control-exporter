import logging
from unittest import mock

import pytest
import yaml
from click.testing import CliRunner

from py_air_control_exporter import main


def test_help():
    result = CliRunner().invoke(main.main, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_unknown_no_targets(tmp_path, caplog):
    config = tmp_path / "config.yaml"
    config_content = yaml.dump({"targets": {}})
    config.write_text(config_content)
    result = CliRunner().invoke(main.main, [f"--config={config}"])
    assert result.exit_code == 1
    assert "No targets specified." in caplog.at_level(logging.ERROR).text


def test_unknown_protocol_exit_code(tmp_path):
    config = tmp_path / "config.yaml"
    config_content = yaml.dump(
        {"targets": {"target1": {"host": "1.2.3.4", "protocol": "foobar"}}},
    )
    config.write_text(config_content)
    result = CliRunner().invoke(main.main, [f"--config={config}"])
    assert result.exit_code == 1


def test_main(mock_create_app, mock_create_targets):
    """Check that the exporter Flask app is created with all the given parameters"""
    result = CliRunner().invoke(
        main.main,
        [
            "--host",
            "192.168.1.123",
            "--protocol",
            "http",
            "--listen-address",
            "1.2.3.4",
            "--listen-port",
            "12345",
        ],
    )
    assert result.exit_code == 0
    mock_create_targets.assert_called_once_with(
        {"192.168.1.123": {"host": "192.168.1.123", "protocol": "http"}}
    )
    expected_targets = mock_create_targets.return_value
    mock_create_app.assert_called_once_with(expected_targets)
    mock_create_app.return_value.run.assert_called_once_with(host="1.2.3.4", port=12345)


def test_unknown_protocol():
    """Check that failure is reporter if an invalid protocol is provided"""
    result = CliRunner(mix_stderr=False).invoke(
        main.main,
        ["--host", "192.168.1.123", "--protocol", "foobar"],
    )
    assert result.exit_code != 0
    assert "--protocol" in result.stderr


def test_unknown_protocol_in_config(caplog):
    """Check that error is logged when config contains unknown protocol"""
    targets_config = {"test": {"host": "1.2.3.4", "protocol": "invalid"}}
    result = main.create_targets(targets_config)
    assert result is None
    assert "Unknown protocol 'invalid' for target 'test'" in caplog.text
    assert "Known protocols:" in caplog.text


@pytest.mark.usefixtures("mock_create_app")
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


def test_default_parameters(mock_create_app, mock_create_targets):
    """Check that the exporter Flask app is created with the given hostname and default
    parameters
    """
    result = CliRunner().invoke(main.main, ["--host", "192.168.1.123"])
    assert result.exit_code == 0
    mock_create_targets.assert_called_once_with(
        {"192.168.1.123": {"host": "192.168.1.123", "protocol": "http"}}
    )
    mock_create_app.return_value.run.assert_called_once_with(
        host="127.0.0.1", port=9896
    )


def test_create_targets(mocker):
    """Check that the targets dictionary is created and ready to fetch."""
    mock_get_reading = mocker.patch(
        "py_air_control_exporter.fetchers.http_philips.get_reading",
        autospec=True,
    )

    targets_config = {
        "foo": {"host": "1.2.3.4", "protocol": "http"},
        "bar": {"host": "1.2.3.5", "protocol": "http"},
    }
    targets = main.create_targets(targets_config)
    assert isinstance(targets, dict)
    assert len(targets) == 2
    assert "foo" in targets
    assert "bar" in targets

    # Call first fetcher and verify arguments
    targets["foo"].fetcher()
    mock_get_reading.assert_called_with("1.2.3.4")

    # Call second fetcher and verify arguments
    targets["bar"].fetcher()
    mock_get_reading.assert_called_with("1.2.3.5")


@pytest.fixture(name="mock_create_app")
def _mock_create_app(mocker):
    return mocker.patch(
        "py_air_control_exporter.app.create_app",
        return_value=mock.Mock(),
        autospec=True,
    )


@pytest.fixture(name="mock_create_targets")
def _mock_create_targets(mocker):
    return mocker.patch(
        "py_air_control_exporter.main.create_targets",
        autospec=True,
    )
