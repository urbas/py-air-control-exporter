from py_air_control_exporter import fetchers_api
from py_air_control_exporter.fetchers import coap_philips, http_philips

KNOWN_FETCHERS: dict[str, fetchers_api.FetcherCreator] = {
    "http": http_philips.create_fetcher,
    "coap": coap_philips.create_fetcher,
}
