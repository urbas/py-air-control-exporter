from py_air_control_exporter.fetchers import api, http_philips

KNOWN_FETCHERS: dict[str, api.FetcherCreator] = {
    "http": http_philips.create_fetcher,
}
