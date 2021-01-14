from unittest import TestCase

from aircraft.deploys.ubuntu.models.v1beta2 import DnsmasqData


class DnsmasqDataTest(TestCase):

    def test__default_to_empty_list_if_interfaces_not_provided(self):
        assert DnsmasqData().interfaces == []
