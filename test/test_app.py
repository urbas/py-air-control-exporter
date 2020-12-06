from unittest import mock

from py_air_control_exporter import app


@mock.patch("py_air_control_exporter.metrics.PyAirControlCollector")
def test_create_app(mock_collector):
    """
    check that we can create an exporter with explicit host and protocol parameters
    """
    app.create_app(host="1.2.3.4", protocol="foobar")
    mock_collector.assert_called_once_with(host="1.2.3.4", protocol="foobar")
