from unittest import mock
import pytest
from py_air_control_exporter import metrics


@pytest.fixture(name="mock_fetcher")
def _mock_fetcher(mocker):
    yield mock.MagicMock(spec=metrics.StatusFetcher)
