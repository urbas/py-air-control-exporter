import click
import logging

from py_air_control_exporter import app, metrics, py_air_fetcher
from py_air_control_exporter.logging import LOG


@click.command()
@click.option(
    "-v", "--verbose", default=0, count=True, help="Increase verbosity level."
)
@click.option("-q", "--quiet", default=0, count=True, help="Decrease verbosity level.")
@click.option(
    "--host", required=True, help="The hostname of the air purifier to monitor."
)
@click.option(
    "--protocol",
    default=py_air_fetcher.HTTP_PROTOCOL,
    type=click.Choice(
        [
            py_air_fetcher.HTTP_PROTOCOL,
            py_air_fetcher.COAP_PROTOCOL,
            py_air_fetcher.PLAIN_COAP_PROTOCOL,
        ],
        case_sensitive=False,
    ),
    show_default=True,
    help="The protocol to use when communicating with the air purifier.",
)
@click.option(
    "--listen-address",
    default="0.0.0.0",
    help="The address on which to listen for HTTP requests.",
    show_default=True,
)
@click.option(
    "--listen-port",
    default=9896,
    help="The port on which to listen for HTTP requests.",
    show_default=True,
)
def main(host, protocol, listen_address, listen_port, verbose, quiet):
    setup_logging(verbose - quiet)
    LOG.info("Listening on %s:%d", listen_address, listen_port)
    status_fetcher = create_status_fetcher(host, protocol)
    app.create_app(status_fetcher).run(host=listen_address, port=listen_port)


def setup_logging(verbosity_level: int) -> None:
    """Configure logging based on verbosity level."""
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
    log_level = min(
        max(logging.DEBUG, logging.WARNING - (verbosity_level * 10)), logging.ERROR
    )
    logging.getLogger().setLevel(log_level)


def create_status_fetcher(
    host: str, protocol: str | None = None
) -> metrics.StatusFetcher:
    return lambda: py_air_fetcher.get_status(host, protocol)
