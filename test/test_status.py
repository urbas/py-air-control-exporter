from philips_air_purifier_exporter.status import fan_speed_to_int, is_on
from test import status_responses


def test_fan_speed_to_int():
    assert 0 == fan_speed_to_int(status_responses.SLEEP_STATUS["om"])
    assert 1 == fan_speed_to_int(status_responses.SPEED_1_STATUS["om"])
    assert 2 == fan_speed_to_int(status_responses.SPEED_2_STATUS["om"])
    assert 3 == fan_speed_to_int(status_responses.SPEED_3_STATUS["om"])
    assert 4 == fan_speed_to_int(status_responses.TURBO_STATUS["om"])


def test_is_on():
    assert not is_on(status_responses.OFF_STATUS)
    assert is_on(status_responses.SLEEP_STATUS)
    assert is_on(status_responses.TURBO_STATUS)
