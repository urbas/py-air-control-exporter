import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
import yaml

from py_air_control_exporter import app, fetcher_registry, fetchers_api, metrics


@dataclass(frozen=True)
class Target:
    host: str
    fetcher: fetchers_api.Fetcher


LOG = logging.getLogger(__name__)


@click.command()
@click.option(
    "-v",
    "--verbose",
    default=0,
    count=True,
    help="Increase verbosity level.",
)
@click.option("-q", "--quiet", default=0, count=True, help="Decrease verbosity level.")
@click.option(
    "--host",
    help="The hostname of the air purifier to monitor. If --name is not provided, "
    "this value will also be used as the name label in metrics.",
)
@click.option(
    "--name",
    help="Optional name to use as label in metrics instead of the hostname.",
)
@click.option(
    "--protocol",
    default="http",
    type=click.Choice(
        tuple(fetcher_registry.get_known_protocols()), case_sensitive=False
    ),
    show_default=True,
    help="The protocol to use when communicating with the air purifier "
    "(used only when `--host` is provided).",
)
@click.option(
    "--listen-address",
    default="127.0.0.1",
    help="The address on which to listen for HTTP requests.",
    show_default=True,
)
@click.option(
    "--listen-port",
    default=9896,
    help="The port on which to listen for HTTP requests.",
    show_default=True,
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to configuration file.",
)
def main(host, name, protocol, listen_address, listen_port, config, verbose, quiet):  # noqa: PLR0913
    setup_logging(verbose - quiet)
    LOG.info("Listening on %s:%d", listen_address, listen_port)
    config_data = load_config(config)
    targets_config = config_data.get("targets", {}) if config_data else {}

    if host:
        targets_config[name or host] = {"host": host, "protocol": protocol}

    targets = create_targets(targets_config)

    if targets is None:
        sys.exit(1)

    if not targets:
        LOG.error("No targets specified. Please specify at least one target.")
        sys.exit(1)

    readings_source = create_readings_source(targets)
    app.create_app(readings_source).run(host=listen_address, port=listen_port)


def setup_logging(verbosity_level: int) -> None:
    """Configure logging based on verbosity level."""
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
    log_level = min(
        max(logging.DEBUG, logging.WARNING - (verbosity_level * 10)),
        logging.ERROR,
    )
    logging.getLogger().setLevel(log_level)


def load_config(config_path: Path | None) -> dict[str, Any]:
    """Load configuration from yaml file if provided, otherwise return empty dict."""
    if config_path is None:
        return {}

    with config_path.open() as f:
        return yaml.safe_load(f)


def create_readings_source(
    targets: dict[str, Target],
) -> metrics.ReadingsSource:
    def _fetch() -> dict[str, fetchers_api.TargetReading]:
        target_readings = {}
        for name, target in targets.items():
            target_reading = None
            try:
                target_reading = target.fetcher()
            except Exception as ex:
                LOG.error(
                    "Failed to sample the air quality from target '%s'. Error: %s",
                    name,
                    ex,
                )
                LOG.debug("Exception stack trace:", exc_info=True)
                continue

            if target_reading is None:
                continue

            target_readings[name] = target_reading
        return target_readings

    return _fetch


def create_targets(
    targets_config: dict[str, dict] | None = None,
) -> dict[str, Target] | None:
    targets = {}

    if targets_config:
        for name, target_config in targets_config.items():
            fetcher_config = fetchers_api.FetcherCreatorArgs(
                target_host=target_config["host"],
                target_name=name,
            )
            protocol = target_config["protocol"]

            try:
                targets[name] = Target(
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
