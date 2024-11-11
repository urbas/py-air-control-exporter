from collections.abc import Iterable

from flask.testing import FlaskClient
from prometheus_client import Metric
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample

from py_air_control_exporter import app, metrics


def test_metrics(mock_target):
    """Metrics endpoint produces the expected metrics"""
    target, mock_func = mock_target
    mock_func.return_value = metrics.TargetReading(
        status=metrics.Status(fan_speed=0, iaql=1, is_manual=True, is_on=True, pm25=2),
        filters={
            "0": metrics.Filter(hours=0, filter_type=""),
            "1": metrics.Filter(hours=185, filter_type="A3"),
            "2": metrics.Filter(hours=2228, filter_type="C7"),
        },
    )

    samples = _get_metrics(app.create_app({"foo": target}).test_client())

    common_labels = {"host": "foo", "name": "some-name"}
    expected_samples = [
        Sample("py_air_control_air_quality", common_labels, value=1.0),
        Sample("py_air_control_is_manual", common_labels, value=1.0),
        Sample("py_air_control_is_on", common_labels, value=1.0),
        Sample("py_air_control_pm25", common_labels, value=2.0),
        Sample("py_air_control_speed", common_labels, value=0.0),
        Sample(
            "py_air_control_filter_hours",
            {**common_labels, "id": "0", "type": ""},
            value=0.0,
        ),
        Sample(
            "py_air_control_filter_hours",
            {**common_labels, "id": "1", "type": "A3"},
            value=185.0,
        ),
        Sample(
            "py_air_control_filter_hours",
            {**common_labels, "id": "2", "type": "C7"},
            value=2228.0,
        ),
    ]

    for expected_sample in expected_samples:
        assert expected_sample in samples


def test_metrics_failure(mock_target):
    """Metrics endpoint should produce a sampling error counter on error"""
    target, mock_func = mock_target
    mock_func.side_effect = Exception()
    test_client = app.create_app({"foo": target}).test_client()
    response = test_client.get("/metrics")
    assert (
        b'py_air_control_sampling_error_total{host="foo",name="some-name"} 2.0\n'
        in response.data
    )
    response = test_client.get("/metrics")
    assert (
        b'py_air_control_sampling_error_total{host="foo",name="some-name"} 3.0\n'
        in response.data
    )


def test_metrics_fetched_again(mock_target):
    """Check that status is fetched every time metrics are pulled"""
    target, mock_func = mock_target
    assert mock_func.call_count == 0
    test_client = app.create_app({"foo": target}).test_client()
    assert mock_func.call_count == 1
    test_client.get("/metrics")
    assert mock_func.call_count == 2
    test_client.get("/metrics")
    assert mock_func.call_count == 3


def _get_metrics(client: FlaskClient) -> list[Sample]:
    actual_metrics = _to_metrics(client.get("/metrics"))
    return [sample for metric in actual_metrics for sample in metric.samples]


def _to_metrics(response) -> Iterable[Metric]:
    return text_string_to_metric_families(response.data.decode("utf-8"))
