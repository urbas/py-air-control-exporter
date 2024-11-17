from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class AirQuality:
    iaql: float  # IAI allergen index
    pm25: float


@dataclass(frozen=True)
class ControlInfo:
    fan_speed: float
    is_manual: bool
    is_on: bool


@dataclass(frozen=True)
class Filter:
    hours: float  # Hours remaining before replacement
    filter_type: str


@dataclass(frozen=True)
class TargetReading:
    air_quality: AirQuality | None
    control_info: ControlInfo | None
    filters: dict[str, Filter] | None


Fetcher = Callable[[], TargetReading | None]


@dataclass(frozen=True)
class FetcherCreatorArgs:
    target_host: str
    target_name: str


FetcherCreator = Callable[[FetcherCreatorArgs], Fetcher]
