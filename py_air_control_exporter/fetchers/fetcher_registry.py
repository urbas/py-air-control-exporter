from py_air_control_exporter import fetchers_api
from py_air_control_exporter.fetchers import http_philips

KNOWN_FETCHERS: dict[str, fetchers_api.FetcherCreator] = {
    "http": http_philips.create_fetcher,
}
