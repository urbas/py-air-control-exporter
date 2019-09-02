import logging
from os import environ
from flask import Blueprint, abort
from flask.json import jsonify
from philips_air_purifier_exporter.comms import get_status
from philips_air_purifier_exporter.prometheus import to_metrics


API = Blueprint("metrics", __name__, url_prefix="/metrics")
HOST_ENV_VAR = "PHILIPS_AIR_PURIFIER_HOST"


@API.route("")
def get():
    try:
        purifier_host = environ[HOST_ENV_VAR]
    except KeyError:
        logging.error(
            "Please specify the host address of the Philips Air Purifier via the environment variable %s",
            HOST_ENV_VAR,
        )
        return abort(500)
    try:
        return to_metrics(get_status(purifier_host))
    except Exception as ex:
        logging.error(
            "Could not read values from Philips Air Purifier %s. Error: %s",
            purifier_host,
            ex,
        )
        return abort(501)
