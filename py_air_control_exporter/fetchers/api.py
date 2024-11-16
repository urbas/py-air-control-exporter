from collections.abc import Callable
from dataclasses import dataclass

from py_air_control_exporter import metrics


@dataclass(frozen=True)
class FetcherCreatorArgs:
    target_host: str
    target_name: str


FetcherCreator = Callable[[FetcherCreatorArgs], metrics.Fetcher]
