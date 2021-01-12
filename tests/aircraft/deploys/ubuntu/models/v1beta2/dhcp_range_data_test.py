import pytest
from unittest import TestCase

from aircraft.deploys.ubuntu.models.v1beta2 import DhcpRangeData


class DhcpRangeDataTest(TestCase):

    def test__raises_a_value_error_when_end_is_less_than_start(self):
        with pytest.raises(ValueError):
            DhcpRangeData(
                start='192.168.100.200',
                end='192.168.100.150',
            )
