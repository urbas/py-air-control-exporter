import itertools
import logging
from collections import defaultdict
from collections.abc import Callable, Iterable

import prometheus_client.core
from prometheus_client import Metric, registry

from py_air_control_exporter import fetchers_api

LOG = logging.getLogger(__name__)


ReadingsSource = Callable[[], dict[str, fetchers_api.TargetReading]]


class PyAirControlCollector(registry.Collector):
    def __init__(self, readings_source: ReadingsSource):
        self._readings_source = readings_source
        self._error_counters = defaultdict(int)

    def collect(self):
        target_readings = self._readings_source()

        return itertools.chain(
            self._sampling_error(target_readings),
            self._air_quality_metrics(target_readings),
            self._control_info_metrics(target_readings),
            self._get_filters_metrics(target_readings),
        )

    def _sampling_error(
        self, target_readings: dict[str, fetchers_api.TargetReading]
    ) -> Iterable[Metric]:
        sampling_error = prometheus_client.core.CounterMetricFamily(
            "py_air_control_sampling_error",
            "Counts the number of times sampling air quality metrics failed.",
            labels=["host", "name"],
        )
        for name, target_reading in target_readings.items():
            if target_reading.has_errors:
                self._error_counters[name] += 1
            sampling_error.add_metric(
                [target_reading.host, name], self._error_counters[name]
            )
        return [sampling_error]

    def _air_quality_metrics(
        self, target_readings: dict[str, fetchers_api.TargetReading]
    ) -> Iterable[Metric]:
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

        for name, target_reading in target_readings.items():
            if target_reading is None:
                continue
            air_quality = target_reading.air_quality
            if air_quality is None:
                LOG.info("No air quality information from air quality host '%s'.", name)
                continue

            LOG.debug(
                "Got the following air quality information from host '%s': %s",
                target_reading.host,
                air_quality,
            )
            iaql.add_metric([target_reading.host, name], air_quality.iaql)
            pm25.add_metric([target_reading.host, name], air_quality.pm25)

        return [iaql, pm25]

    def _control_info_metrics(
        self, target_readings: dict[str, fetchers_api.TargetReading]
    ) -> Iterable[Metric]:
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

        for name, target_reading in target_readings.items():
            if target_reading is None:
                continue
            control_info = target_reading.control_info
            if control_info is None:
                LOG.info("No control info for air quality host '%s'.", name)
                continue

            LOG.debug(
                "Got the following control info from host '%s': %s",
                target_reading.host,
                control_info,
            )
            is_manual.add_metric(
                [target_reading.host, name], 1 if control_info.is_manual else 0
            )
            is_on.add_metric(
                [target_reading.host, name], 1 if control_info.is_on else 0
            )
            speed.add_metric([target_reading.host, name], control_info.fan_speed)

        return [is_manual, is_on, speed]

    def _get_filters_metrics(
        self, target_readings: dict[str, fetchers_api.TargetReading]
    ) -> Iterable[Metric]:
        filter_metric_family = prometheus_client.core.GaugeMetricFamily(
            "py_air_control_filter_hours",
            "The number of values left before the filter has to be replaced or cleaned",
            labels=["host", "name", "id", "type"],
        )

        for name, target_reading in target_readings.items():
            if target_reading is None:
                continue
            filters = target_reading.filters
            if filters is None:
                LOG.info("No filter information for air quality host '%s'.", name)
                continue

            LOG.debug(
                "Got the following filters for host '%s': %s",
                target_reading.host,
                filters,
            )
            for filter_id, filter_info in filters.items():
                filter_metric_family.add_metric(
                    [
                        target_reading.host,
                        name,
                        filter_id,
                        filter_info.filter_type,
                    ],
                    filter_info.hours,
                )

        return [filter_metric_family]
