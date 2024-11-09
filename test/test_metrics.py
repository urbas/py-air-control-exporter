from py_air_control_exporter import app, metrics


def test_metrics_no_data(mock_fetcher):
    """metrics endpoint should produce a sampling error counter on error"""
    mock_fetcher.return_value = None
    test_client = app.create_app(mock_fetcher).test_client()
    response = test_client.get("/metrics")
    assert b"py_air_control_sampling_error_total 2.0\n" in response.data


def test_metrics_empty(mock_fetcher):
    """metrics endpoint should produce empty metrics on empty status"""
    mock_fetcher.return_value = metrics.AirControlStatus(status=None, filters=None)
    test_client = app.create_app(mock_fetcher).test_client()
    response = test_client.get("/metrics")
    assert response.data == b""
