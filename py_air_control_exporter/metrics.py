import logging
from os import environ

import prometheus_client.core
from pyairctrl import coap_client, http_client, plain_coap_client

HOST_ENV_VAR = "PY_AIR_CONTROL_HOST"
PROTOCOL_ENV_VAR = "PY_AIR_CONTROL_PROTOCOL"
HTTP_PROTOCOL = "http"
COAP_PROTOCOL = "coap"
PLAIN_COAP_PROTOCOL = "plain_coap"
_FAN_SPEED_TO_INT = {"s": 0, "1": 1, "2": 2, "3": 3, "t": 4}


class PyAirControlCollector:
    def __init__(self, host=None, protocol=None):
        self._host = host
        self._protocol = protocol
        self._error_counter = 0

    def collect(self):
        status = None
        try:
            status = get_status(host=self._host, protocol=self._protocol)
        except Exception as ex:
            logging.error("Failed to sample the air quality. Error: %s", ex)
            yield self._sampling_error()
            return None

        if status is None:
            yield self._sampling_error()
            return None

        logging.debug("Got the following status from py-air-control: %s", status)
        yield prometheus_client.core.GaugeMetricFamily(
            "py_air_control_air_quality",
            "IAI allergen index from 1 to 12, where 1 indicates best air quality.",
            value=status["iaql"],
        )
        yield prometheus_client.core.GaugeMetricFamily(
            "py_air_control_is_manual",
            "Value '1' indicates manual mode while value '0' indicates "
            "automatic mode.",
            value=1 if is_manual_mode(status) else 0,
        )
        yield prometheus_client.core.GaugeMetricFamily(
            "py_air_control_is_on",
            "Value '1' indicates that the air purifier is turned on while value "
            "'0' indicates it's turned off.",
            value=1 if is_on(status) else 0,
        )
        yield prometheus_client.core.GaugeMetricFamily(
            "py_air_control_pm25",
            "Micrograms of PM2.5 particles per cubic metre.",
            value=status["pm25"],
        )
        yield prometheus_client.core.GaugeMetricFamily(
            "py_air_control_speed",
            "The fan speed setting (0 is sleep, 1-3 correspond to level settings, "
            "and 4 stands for 'turbo').",
            value=fan_speed_to_int(status),
        )

    def _sampling_error(self):
        self._error_counter += 1
        return prometheus_client.core.CounterMetricFamily(
            "py_air_control_sampling_error",
            "Counts the number of times sampling air quality metrics failed.",
            value=self._error_counter,
        )


def get_status(host=None, protocol=None):
    try:
        host = host or environ[HOST_ENV_VAR]
    except KeyError:
        logging.error(
            "Please specify the host address of the air control device via the "
            "environment variable %s",
            HOST_ENV_VAR,
        )
        return None

    protocol = protocol or environ.get(PROTOCOL_ENV_VAR, HTTP_PROTOCOL)
    client = get_client(protocol, host)
    if client is None:
        return None

    try:
        return client.get_status()
    except Exception as ex:
        logging.error(
            "Could not read values from air control device %s. Error: %s",
            host,
            ex,
        )
        return None


def get_client(protocol, host):
    if protocol == HTTP_PROTOCOL:
        return http_client.HTTPAirClient(host)
    if protocol == COAP_PROTOCOL:
        return coap_client.CoAPAirClient(host)
    if protocol == PLAIN_COAP_PROTOCOL:
        return plain_coap_client.PlainCoAPAirClient(host)
    logging.error(
        "Unknown protocol '%s'. Please set the environment variable '%s' to one of the "
        "following: %s, %s, %s",
        protocol,
        PROTOCOL_ENV_VAR,
        HTTP_PROTOCOL,
        COAP_PROTOCOL,
        PLAIN_COAP_PROTOCOL,
    )
    return None


def fan_speed_to_int(status):
    return _FAN_SPEED_TO_INT[status["om"]]


def is_on(status):
    return status["pwr"] == "1"


def is_manual_mode(status):
    return status["mode"] == "M"
