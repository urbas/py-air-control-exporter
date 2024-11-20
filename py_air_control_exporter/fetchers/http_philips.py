import logging

from pyairctrl import http_client

from py_air_control_exporter import fetchers_api

LOG = logging.getLogger(__name__)

_FAN_SPEED_TO_INT = {"s": 0, "1": 1, "2": 2, "3": 3, "t": 4}


def create_fetcher(config: fetchers_api.FetcherCreatorArgs) -> fetchers_api.Fetcher:
    return lambda target_host=config.target_host: get_reading(target_host)


def get_reading(host: str) -> fetchers_api.TargetReading:
    client = http_client.HTTPAirClient(host)

    try:
        status_data = client.get_status() or {}
        filters_data = client.get_filters() or {}

        return fetchers_api.TargetReading(
            host=host,
            has_errors=False,
            air_quality=create_air_quality(status_data),
            control_info=create_control_info(status_data),
            filters=create_filter_info(filters_data),
        )

    except Exception as ex:
        LOG.error(
            "Could not read values from air control device %s. Error: %s", host, ex
        )
        LOG.debug("Exception stack trace:", exc_info=True)
        return fetchers_api.TargetReading(host=host, has_errors=True)


def create_air_quality(status_data: dict) -> fetchers_api.AirQuality:
    return fetchers_api.AirQuality(iaql=status_data["iaql"], pm25=status_data["pm25"])


def create_control_info(status_data: dict) -> fetchers_api.ControlInfo:
    return fetchers_api.ControlInfo(
        fan_speed=_FAN_SPEED_TO_INT[status_data["om"]],
        is_manual=status_data["mode"] == "M",
        is_on=status_data["pwr"] == "1",
    )


def create_filter_info(filters_data: dict) -> dict[str, fetchers_api.Filter]:
    filters: dict[str, fetchers_api.Filter] = {}
    for key, value in filters_data.items():
        if key.startswith("fltsts"):
            filter_id = key[6:]
            filters[filter_id] = fetchers_api.Filter(
                hours=value,
                filter_type=filters_data.get(f"fltt{filter_id}", ""),
            )

    return filters
