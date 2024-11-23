import logging
from collections.abc import Callable
from dataclasses import dataclass

from py_air_control_exporter import fetcher_registry, fetchers_api

LOG = logging.getLogger(__name__)

ReadingsSource = Callable[[], dict[str, fetchers_api.TargetReading]]


@dataclass(frozen=True)
class _Target:
    host: str
    fetcher: fetchers_api.Fetcher


def from_config(targets_config: dict[str, dict]) -> ReadingsSource | None:
    targets = _create_targets(targets_config)
    if not targets:
        return None
    return _create_readings_source(targets)


def _create_readings_source(
    targets: dict[str, _Target],
) -> ReadingsSource:
    def _fetch() -> dict[str, fetchers_api.TargetReading]:
        return {name: target.fetcher() for name, target in targets.items()}

    return _fetch


def _create_targets(
    targets_config: dict[str, dict],
) -> dict[str, _Target] | None:
    targets = {}

    for name, target_config in targets_config.items():
        fetcher_config = fetchers_api.FetcherCreatorArgs(
            target_host=target_config["host"],
            target_name=name,
        )
        protocol = target_config["protocol"]

        try:
            targets[name] = _Target(
                host=fetcher_config.target_host,
                fetcher=fetcher_registry.create_fetcher(protocol, fetcher_config),
            )
        except fetcher_registry.UnknownProtocolError:
            LOG.error(
                "Unknown protocol '%s' for target '%s'. Known protocols: %s",
                protocol,
                name,
                ", ".join(fetcher_registry.get_known_protocols()),
            )
            return None

    return targets
