from py_air_control_exporter import readings_source
from test import conftest


def test_from_config(mocker):
    """Check that the readings source is created from config and returns a reading"""
    expected_reading = conftest.SOME_READINGS["full"]
    mocker.patch(
        "py_air_control_exporter.fetchers.http_philips.get_reading",
        autospec=True,
        return_value=expected_reading,
    )
    source = readings_source.from_config(
        {"foo": {"host": expected_reading.host, "protocol": "http"}}
    )
    assert source is not None
    assert source() == {"foo": expected_reading}


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
    targets = readings_source.create_targets(targets_config)
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


def test_unknown_protocol_in_config(caplog):
    """Check that error is logged when config contains unknown protocol"""
    targets_config = {"test": {"host": "1.2.3.4", "protocol": "invalid"}}
    result = readings_source.create_targets(targets_config)
    assert result is None
    assert "Unknown protocol 'invalid' for target 'test'" in caplog.text
    assert "Known protocols:" in caplog.text
