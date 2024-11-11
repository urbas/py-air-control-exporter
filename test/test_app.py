from py_air_control_exporter import app, metrics


def test_metrics(mock_fetcher):
    """Metrics endpoint produces the expected metrics"""
    mock_fetcher.return_value = metrics.AirControlStatus(
        status=metrics.Status(fan_speed=0, iaql=1, is_manual=True, is_on=True, pm25=2),
        filters=metrics.Filters(
            filters={
                "0": metrics.Filter(hours=0, filter_type=""),
                "1": metrics.Filter(hours=185, filter_type="A3"),
                "2": metrics.Filter(hours=2228, filter_type="C7"),
            },
        ),
    )
    response = app.create_app(mock_fetcher).test_client().get("/metrics")
    assert b"py_air_control_air_quality 1.0\n" in response.data
    assert b"py_air_control_is_manual 1.0\n" in response.data
    assert b"py_air_control_is_on 1.0\n" in response.data
    assert b"py_air_control_pm25 2.0\n" in response.data
    assert b"py_air_control_speed 0.0\n" in response.data
    assert b'py_air_control_filter_hours{id="0",type=""} 0.0\n' in response.data
    assert b'py_air_control_filter_hours{id="1",type="A3"} 185.0\n' in response.data
    assert b'py_air_control_filter_hours{id="2",type="C7"} 2228.0\n' in response.data
    assert b"IAI allergen index" in response.data


def test_metrics_failure(mock_fetcher):
    """Metrics endpoint should produce a sampling error counter on error"""
    mock_fetcher.side_effect = Exception()
    test_client = app.create_app(mock_fetcher).test_client()
    response = test_client.get("/metrics")
    assert b"py_air_control_sampling_error_total 2.0\n" in response.data
    response = test_client.get("/metrics")
    assert b"py_air_control_sampling_error_total 3.0\n" in response.data


def test_metrics_fetched_again(mock_fetcher):
    """Check that status is fetched every time metrics are pulled"""
    assert mock_fetcher.call_count == 0
    test_client = app.create_app(mock_fetcher).test_client()
    assert mock_fetcher.call_count == 1
    test_client.get("/metrics")
    assert mock_fetcher.call_count == 2
    test_client.get("/metrics")
    assert mock_fetcher.call_count == 3
