from unittest import mock

import pytest

from py_air_control_exporter import metrics


@pytest.fixture(name="mock_target")
def _mock_target():
    mock_func = mock.MagicMock()
    return metrics.Target(host="foo", name="some-name", fetcher=mock_func), mock_func
