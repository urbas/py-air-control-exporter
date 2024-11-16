from pyairctrl import http_client

from py_air_control_exporter.fetchers.api import FetcherCreatorArgs
from py_air_control_exporter.logging import LOG
from py_air_control_exporter.metrics import Fetcher, Filter, Status, TargetReading

_FAN_SPEED_TO_INT = {"s": 0, "1": 1, "2": 2, "3": 3, "t": 4}


def create_fetcher(config: FetcherCreatorArgs) -> Fetcher:
    return lambda target_host=config.target_host: get_reading(target_host)


def get_reading(
    host: str,
) -> TargetReading | None:
    client = http_client.HTTPAirClient(host)

    try:
        status_data = client.get_status() or {}
        filters_data = client.get_filters() or {}

        status = create_status(status_data)
        filters = create_filter_info(filters_data)

        return TargetReading(status=status, filters=filters)
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


def create_filter_info(filters_data: dict) -> dict[str, Filter]:
    filters: dict[str, Filter] = {}
    for key, value in filters_data.items():
        if key.startswith("fltsts"):
            filter_id = key[6:]
            filters[filter_id] = Filter(
                hours=value,
                filter_type=filters_data.get(f"fltt{filter_id}", ""),
            )

    return filters
