from py_air_control_exporter import app, metrics


def test_metrics_no_data(mock_target):
    """Metrics endpoint should produce a sampling error counter on error"""
    target, mock_func = mock_target
    mock_func.return_value = None
    test_client = app.create_app({"foo": target}).test_client()
    response = test_client.get("/metrics")
    assert (
        b'py_air_control_sampling_error_total{host="foo",name="some-name"} 2.0\n'
        in response.data
    )


def test_metrics_empty(mock_target):
    """Metrics endpoint should produce empty metrics on empty status"""
    target, mock_func = mock_target
    mock_func.return_value = metrics.TargetReading(status=None, filters=None)
    test_client = app.create_app({"foo": target}).test_client()
    response = test_client.get("/metrics")
    assert b"HELP py_air_control_sampling_error_total" in response.data
