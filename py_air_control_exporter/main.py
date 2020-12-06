import click

from py_air_control_exporter import app, metrics


@click.command()
@click.option(
    "--host", required=True, help="The hostname of the air purifier to monitor."
)
@click.option(
    "--protocol",
    default=metrics.HTTP_PROTOCOL,
    type=click.Choice(
        [metrics.HTTP_PROTOCOL, metrics.COAP_PROTOCOL, metrics.PLAIN_COAP_PROTOCOL],
        case_sensitive=False,
    ),
    show_default=True,
    help="The protocol to use when communicating with the air purifier.",
)
@click.option(
    "--listen-address",
    default="0.0.0.0",
    help="The address on which to listen for HTTP requests.",
)
@click.option(
    "--listen-port",
    default=9896,
    help="The port on which to listen for HTTP requests.",
)
def main(host, protocol, listen_address, listen_port):
    app.create_app(host=host, protocol=protocol).run(
        host=listen_address, port=listen_port
    )
