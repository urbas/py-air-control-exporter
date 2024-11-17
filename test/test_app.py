from prometheus_client.samples import Sample

from py_air_control_exporter import app
from test import conftest


def test_metrics(mock_readings_source):
    """Metrics endpoint produces the expected metrics"""
    client = app.create_app(mock_readings_source).test_client()
    samples = conftest.get_samples(client)

    common_labels = {"host": "1.2.3.4", "name": "full"}
    expected_samples = [
        Sample("py_air_control_air_quality", common_labels, value=3.0),
        Sample("py_air_control_is_manual", common_labels, value=1.0),
        Sample("py_air_control_is_on", common_labels, value=1.0),
        Sample("py_air_control_pm25", common_labels, value=5.0),
        Sample("py_air_control_speed", common_labels, value=2.0),
        Sample(
            "py_air_control_filter_hours",
            {**common_labels, "id": "0", "type": ""},
            value=42.0,
        ),
        Sample(
            "py_air_control_filter_hours",
            {**common_labels, "id": "1", "type": "A3"},
            value=185.0,
        ),
        Sample(
            "py_air_control_filter_hours",
            {**common_labels, "id": "2", "type": "C7"},
            value=9001.0,
        ),
    ]

    for expected_sample in expected_samples:
        assert expected_sample in samples


def test_metrics_failure(mock_readings_source):
    """Metrics endpoint should increment a sampling error counter on error"""
    test_client = app.create_app(mock_readings_source).test_client()
    labels = {"host": "1.2.3.1", "name": "broken"}
    assert Sample(
        "py_air_control_sampling_error_total", labels, value=2.0
    ) in conftest.get_samples(test_client)
    assert Sample(
        "py_air_control_sampling_error_total", labels, value=3.0
    ) in conftest.get_samples(test_client)


def test_metrics_fetched_again(mock_readings_source):
    """Check that status is fetched every time metrics are pulled"""
    assert mock_readings_source.call_count == 0
    test_client = app.create_app(mock_readings_source).test_client()
    assert mock_readings_source.call_count == 1
    test_client.get("/metrics")
    assert mock_readings_source.call_count == 2
    test_client.get("/metrics")
    assert mock_readings_source.call_count == 3
