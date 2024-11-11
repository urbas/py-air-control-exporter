from os import environ

from pyairctrl import coap_client, http_client, plain_coap_client

from py_air_control_exporter.logging import LOG
from py_air_control_exporter.metrics import AirControlStatus, Filter, Filters, Status

HOST_ENV_VAR = "PY_AIR_CONTROL_HOST"
PROTOCOL_ENV_VAR = "PY_AIR_CONTROL_PROTOCOL"
HTTP_PROTOCOL = "http"
COAP_PROTOCOL = "coap"
PLAIN_COAP_PROTOCOL = "plain_coap"
_FAN_SPEED_TO_INT = {"s": 0, "1": 1, "2": 2, "3": 3, "t": 4}


def get_status(
    host: str | None = None,
    protocol: str | None = None,
) -> AirControlStatus | None:
    try:
        host = host or environ[HOST_ENV_VAR]
    except KeyError:
        LOG.error(
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
        status_data = client.get_status() or {}
        filters_data = client.get_filters() or {}

        status = create_status(status_data)
        filters = create_filter_info(filters_data)

        return AirControlStatus(status=status, filters=filters)
    except Exception as ex:
        LOG.error(
            "Could not read values from air control device %s. Error: %s",
            host,
            ex,
        )
        return None


def create_status(status_data: dict) -> Status:
    return Status(
        fan_speed=_FAN_SPEED_TO_INT[status_data["om"]],
        iaql=status_data["iaql"],
        is_manual=status_data["mode"] == "M",
        is_on=status_data["pwr"] == "1",
        pm25=status_data["pm25"],
    )


def create_filter_info(filters_data: dict) -> Filters:
    filters = {}
    for key, value in filters_data.items():
        if key.startswith("fltsts"):
            filter_id = key[6:]
            filters[filter_id] = Filter(
                hours=value,
                filter_type=filters_data.get(f"fltt{filter_id}", ""),
            )

    return Filters(filters=filters)


def get_client(protocol, host):
    if protocol == HTTP_PROTOCOL:
        return http_client.HTTPAirClient(host)
    if protocol == COAP_PROTOCOL:
        return coap_client.CoAPAirClient(host)
    if protocol == PLAIN_COAP_PROTOCOL:
        return plain_coap_client.PlainCoAPAirClient(host)
    LOG.error(
        "Unknown protocol '%s'. Please set the environment variable '%s' to one of the "
        "following: %s, %s, %s",
        protocol,
        PROTOCOL_ENV_VAR,
        HTTP_PROTOCOL,
        COAP_PROTOCOL,
        PLAIN_COAP_PROTOCOL,
    )
    return None
