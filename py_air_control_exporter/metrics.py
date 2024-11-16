import itertools
from collections.abc import Iterable
from dataclasses import dataclass

import prometheus_client.core
from prometheus_client import Metric, registry

from py_air_control_exporter import fetchers_api
from py_air_control_exporter.logging import LOG


@dataclass(frozen=True)
class Target:
    host: str
    name: str
    fetcher: fetchers_api.Fetcher


class PyAirControlCollector(registry.Collector):
    def __init__(self, targets: dict[str, Target]):
        self._targets = targets
        self._error_counters = {target_name: 0 for target_name in targets}

    def collect(self):
        targets_with_errors: set[str] = set()
        target_readings: dict[str, fetchers_api.TargetReading] = {}
        for name, target in self._targets.items():
            target_reading = None
            try:
                target_reading = target.fetcher()
            except Exception as ex:
                LOG.error(
                    "Failed to sample the air quality from target '%s'. Error: %s",
                    name,
                    ex,
                )
                targets_with_errors.add(name)
                continue

            if target_reading is None:
                targets_with_errors.add(name)
                continue

            target_readings[name] = target_reading

        return itertools.chain(
            self._sampling_error(targets_with_errors),
            self._air_quality_metrics(target_readings),
            self._control_info_metrics(target_readings),
            self._get_filters_metrics(target_readings),
        )

    def _sampling_error(self, targets_with_errors: set[str]) -> Iterable[Metric]:
        sampling_error = prometheus_client.core.CounterMetricFamily(
            "py_air_control_sampling_error",
            "Counts the number of times sampling air quality metrics failed.",
            labels=["host", "name"],
        )
        for name in targets_with_errors:
            error_counter = self._error_counters[name] + 1
            self._error_counters[name] = error_counter
            target = self._targets[name]
            sampling_error.add_metric([target.host, target.name], error_counter)
        return [sampling_error]

    def _air_quality_metrics(self, statuses: dict[str, fetchers_api.TargetReading]):
        iaql = prometheus_client.core.GaugeMetricFamily(
            "py_air_control_air_quality",
            "IAI allergen index from 1 to 12, where 1 indicates best air quality.",
            labels=["host", "name"],
        )

        pm25 = prometheus_client.core.GaugeMetricFamily(
            "py_air_control_pm25",
            "Micrograms of PM2.5 particles per cubic metre.",
            labels=["host", "name"],
        )

        for name, full_status in statuses.items():
            air_quality = full_status.air_quality
            if air_quality is None:
                LOG.info("No air quality information from air quality host '%s'.", name)
                continue

            target = self._targets[name]
            LOG.debug(
                "Got the following air quality information from host '%s': %s",
                target.host,
                air_quality,
            )
            iaql.add_metric([target.host, target.name], air_quality.iaql)
            pm25.add_metric([target.host, target.name], air_quality.pm25)

        return [iaql, pm25]

    def _control_info_metrics(self, statuses: dict[str, fetchers_api.TargetReading]):
        is_manual = prometheus_client.core.GaugeMetricFamily(
            "py_air_control_is_manual",
            "Value '1' indicates manual mode while value '0' indicates automatic mode.",
            labels=["host", "name"],
        )

        is_on = prometheus_client.core.GaugeMetricFamily(
            "py_air_control_is_on",
            "Value '1' indicates that the air purifier is turned on while value "
            "'0' indicates it's turned off.",
            labels=["host", "name"],
        )

        speed = prometheus_client.core.GaugeMetricFamily(
            "py_air_control_speed",
            "The fan speed setting (0 is sleep, 1-3 correspond to level settings, "
            "and 4 stands for 'turbo').",
            labels=["host", "name"],
        )

        for name, full_status in statuses.items():
            control_info = full_status.control_info
            if control_info is None:
                LOG.info("No control info for air quality host '%s'.", name)
                continue

            target = self._targets[name]
            LOG.debug(
                "Got the following control info from host '%s': %s",
                target.host,
                control_info,
            )
            is_manual.add_metric(
                [target.host, target.name], 1 if control_info.is_manual else 0
            )
            is_on.add_metric([target.host, target.name], 1 if control_info.is_on else 0)
            speed.add_metric([target.host, target.name], control_info.fan_speed)

        return [is_manual, is_on, speed]

    def _get_filters_metrics(
        self, target_readings: dict[str, fetchers_api.TargetReading]
    ):
        filter_metric_family = prometheus_client.core.GaugeMetricFamily(
            "py_air_control_filter_hours",
            "The number of values left before the filter has to be replaced or cleaned",
            labels=["host", "name", "id", "type"],
        )

        for name, status in target_readings.items():
            filters = status.filters
            if filters is None:
                LOG.info("No filter information for air quality host '%s'.", name)
                continue

            target = self._targets[name]
            LOG.debug(
                "Got the following filters for host '%s': %s",
                target.host,
                filters,
            )
            for filter_id, filter_info in filters.items():
                filter_metric_family.add_metric(
                    [
                        target.host,
                        target.name,
                        filter_id,
                        filter_info.filter_type,
                    ],
                    filter_info.hours,
                )

        return [filter_metric_family]
