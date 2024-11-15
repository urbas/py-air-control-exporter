import prometheus_client
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from py_air_control_exporter import metrics


def create_app(targets: dict[str, metrics.Target]):
    app = Flask(__name__)
    metrics_collector_registry = prometheus_client.CollectorRegistry(auto_describe=True)
    metrics_collector_registry.register(metrics.PyAirControlCollector(targets))
    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app,
        {"/metrics": prometheus_client.make_wsgi_app(metrics_collector_registry)},
    )
    return app
