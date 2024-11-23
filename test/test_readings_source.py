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


def test_unknown_protocol_in_config(caplog):
    """Check that error is logged when config contains unknown protocol"""
    targets_config = {"test": {"host": "1.2.3.4", "protocol": "invalid"}}
    result = readings_source.from_config(targets_config)
    assert result is None
    assert "Unknown protocol 'invalid' for target 'test'" in caplog.text
    assert "Known protocols:" in caplog.text
