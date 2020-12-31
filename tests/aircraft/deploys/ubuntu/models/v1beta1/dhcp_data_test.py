import pytest
from unittest import TestCase

from aircraft.deploys.ubuntu.models.v1beta1 import DhcpData


class DhcpDataTest(TestCase):

    def test__raises_a_value_error_when_range_start_is_out_of_bounds(self):
        with pytest.raises(ValueError):
            DhcpData(
                subnet='192.168.100.0/24',
                ranges=[
                    {
                        'start': '192.168.10.10',
                        'end': '192.168.100.200',
                    }
                ],

                router='192.168.100.1',
                dns_servers=[],
                bootfiles=[],
            )

    def test__raises_a_value_error_when_range_end_is_out_of_bounds(self):
        with pytest.raises(ValueError):
            DhcpData(
                subnet='192.168.100.0/24',
                ranges=[
                    {
                        'start': '192.168.100.10',
                        'end': '192.168.200.200',
                    }
                ],

                router='192.168.100.1',
                dns_servers=[],
                bootfiles=[],
            )
