import itertools
from dataclasses import dataclass
from typing import Callable, Dict, Optional

import prometheus_client.core
from prometheus_client import registry

from py_air_control_exporter.logging import LOG


@dataclass
class Status:
    fan_speed: float  # Integer representation of fan speed
    iaql: float  # IAI allergen index
    is_manual: bool  # True if in manual mode
    is_on: bool  # True if powered on
    pm25: float  # PM2.5 value


@dataclass
class Filter:
    hours: float  # Hours remaining
    type: str  # Filter type


@dataclass
class Filters:
    filters: Dict[str, Filter]  # Filter ID to Filter info


@dataclass
class AirControlStatus:
    status: Optional[Status]
    filters: Optional[Filters]


StatusFetcher = Callable[[], AirControlStatus | None]


class PyAirControlCollector(registry.Collector):
    def __init__(self, status_fetcher: StatusFetcher):
        self._status_fetcher = status_fetcher
        self._error_counter = 0

    def collect(self):
        full_status = None
        try:
            full_status = self._status_fetcher()
        except Exception as ex:
            LOG.error("Failed to sample the air quality. Error: %s", ex)
            return self._sampling_error()

        if full_status is None:
            return self._sampling_error()

        return itertools.chain(
            _get_status_metrics(full_status.status),
            _get_filters_metrics(full_status.filters),
        )

    def _sampling_error(self):
        self._error_counter += 1
        return [
            prometheus_client.core.CounterMetricFamily(
                "py_air_control_sampling_error",
                "Counts the number of times sampling air quality metrics failed.",
                value=self._error_counter,
            )
        ]


def _get_status_metrics(status: Optional[Status]):
    if status is None:
        LOG.warning("Could not retrieve the status from py-air-control.")
        return []
    LOG.debug("Got the following status from py-air-control: %s", status)
    return [
        prometheus_client.core.GaugeMetricFamily(
            "py_air_control_air_quality",
            "IAI allergen index from 1 to 12, where 1 indicates best air quality.",
            value=status.iaql,
        ),
        prometheus_client.core.GaugeMetricFamily(
            "py_air_control_is_manual",
            "Value '1' indicates manual mode while value '0' indicates "
            "automatic mode.",
            value=1 if status.is_manual else 0,
        ),
        prometheus_client.core.GaugeMetricFamily(
            "py_air_control_is_on",
            "Value '1' indicates that the air purifier is turned on while value "
            "'0' indicates it's turned off.",
            value=1 if status.is_on else 0,
        ),
        prometheus_client.core.GaugeMetricFamily(
            "py_air_control_pm25",
            "Micrograms of PM2.5 particles per cubic metre.",
            value=status.pm25,
        ),
        prometheus_client.core.GaugeMetricFamily(
            "py_air_control_speed",
            "The fan speed setting (0 is sleep, 1-3 correspond to level settings, "
            "and 4 stands for 'turbo').",
            value=status.fan_speed,
        ),
    ]


def _get_filters_metrics(filters: Optional[Filters]):
    if filters is None:
        LOG.warning("Could not retrieve filter information from py-air-control.")
        return []
    LOG.debug("Got the following filters from py-air-control: %s", filters)

    filter_metric_family = prometheus_client.core.GaugeMetricFamily(
        "py_air_control_filter_hours",
        "The number of values left before the filter has to be replaced or cleaned",
        labels=["id", "type"],
    )

    for filter_id, filter_info in filters.filters.items():
        filter_metric_family.add_metric(
            [filter_id, filter_info.type],
            filter_info.hours,
        )

    return [filter_metric_family]
