from flask import Flask
from philips_air_purifier_exporter import metrics


def create_app(users=None):
    app = Flask(__name__)
    app.register_blueprint(metrics.API)
    return app