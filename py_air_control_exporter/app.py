from flask import Flask
from py_air_control_exporter import metrics


def create_app():
    app = Flask(__name__)
    app.register_blueprint(metrics.API)
    return app
