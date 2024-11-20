from prometheus_client.samples import Sample

from py_air_control_exporter import app, fetchers_api
from test.conftest import get_samples


def test_metrics(mock_readings_source):
    """Metrics endpoint should produce some metrics"""
    assert Sample(
        "py_air_control_pm25", {"host": "1.2.3.4", "name": "full"}, value=5.0
    ) in get_samples(app.create_app(mock_readings_source).test_client())


def test_metrics_error(mock_readings_source):
    """Metrics endpoint should produce a sampling error counter on error"""
    assert Sample(
        "py_air_control_sampling_error_total",
        {"host": "1.2.3.1", "name": "broken"},
        value=2.0,
    ) in get_samples(app.create_app(mock_readings_source).test_client())


def test_metrics_no_data(mock_readings_source):
    """
    Metrics endpoint should produce only the error counter when target produces no data
    """
    mock_readings_source.return_value = {
        "empty": fetchers_api.TargetReading(host="1.2.3.1")
    }
    assert [
        Sample(
            "py_air_control_sampling_error_total",
            {"host": "1.2.3.1", "name": "empty"},
            value=0.0,
        )
    ] == get_samples(app.create_app(mock_readings_source).test_client())


def test_metrics_empty(mock_readings_source):
    """Metrics endpoint should produce no metrics when there are no targets"""
    mock_readings_source.return_value = {}
    assert not get_samples(app.create_app(mock_readings_source).test_client())
