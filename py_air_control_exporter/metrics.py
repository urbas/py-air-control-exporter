import logging
from os import environ

from flask import Blueprint, abort
from pyairctrl import coap_client, http_air_client, plain_coap_client

from py_air_control_exporter import prometheus

API = Blueprint("metrics", __name__, url_prefix="/metrics")
HOST_ENV_VAR = "PY_AIR_CONTROL_HOST"
PROTOCOL_ENV_VAR = "PY_AIR_CONTROL_PROTOCOL"
HTTP_PROTOCOL = "http"
COAP_PROTOCOL = "coap"
PLAIN_COAP_PROTOCOL = "plain_coap"


@API.route("")
def get():
    try:
        host = environ[HOST_ENV_VAR]
    except KeyError:
        logging.error(
            "Please specify the host address of the air control device via the environment variable %s",
            HOST_ENV_VAR,
        )
        return abort(500)
    protocol = environ.get(PROTOCOL_ENV_VAR, HTTP_PROTOCOL)
    client = get_client(protocol, host)
    if client is None:
        return abort(500)
    try:
        status = client.get_status()
        logging.debug("Got the following status from py-air-control: %s", status)
        return prometheus.to_metrics(status)
    except Exception as ex:
        logging.error(
            "Could not read values from air control device %s. Error: %s",
            host,
            ex,
        )
        return abort(501)


def get_client(protocol, host):
    if protocol == HTTP_PROTOCOL:
        return http_air_client.HTTPAirClient(host)
    if protocol == COAP_PROTOCOL:
        return coap_client.CoAPAirClient(host)
    if protocol == PLAIN_COAP_PROTOCOL:
        return plain_coap_client.PlainCoAPAirClient(host)
    logging.error(
        "Unknown protocol '%s'. Please set the environment variable '%s' to one of the following: %s, %s, %s",
        protocol,
        PROTOCOL_ENV_VAR,
        HTTP_PROTOCOL,
        COAP_PROTOCOL,
        PLAIN_COAP_PROTOCOL,
    )
    return None
