from collections.abc import Iterable

from py_air_control_exporter import fetchers_api
from py_air_control_exporter.fetchers import http_philips

_KNOWN_FETCHERS: dict[str, fetchers_api.FetcherCreator] = {
    "http": http_philips.create_fetcher,
}


class UnknownProtocolError(Exception):
    pass


def get_known_protocols() -> Iterable[str]:
    return _KNOWN_FETCHERS.keys()


def create_fetcher(
    protocol: str, fetcher_config: fetchers_api.FetcherCreatorArgs
) -> fetchers_api.Fetcher:
    fetcher_creator = _KNOWN_FETCHERS.get(protocol)
    if fetcher_creator is None:
        raise UnknownProtocolError
    return fetcher_creator(fetcher_config)
