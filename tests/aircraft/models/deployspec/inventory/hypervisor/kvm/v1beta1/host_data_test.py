import unittest
from uuid import uuid4

from pydantic.error_wrappers import ValidationError
import pytest

from aircraft.models.deployspec.inventory.hypervisor.kvm.v1beta1 import (
    BaseData,
    HostData,
)


class HostDataTest(unittest.TestCase):

    def test__accepts_a_list_of_guests(self):
        guests = [{'name': str(uuid4())} for _ in range(4)]
        data = HostData(guests=guests)

        assert data.guests == guests

    def test__raises_an_error_if_ip_address_is_invalid(self):
        with pytest.raises(ValidationError) as excep_info:
            HostData(ip_address=str(uuid4()))

        assert excep_info.value.errors()[0]['type'] \
            == 'value_error.invalidipaddress', \
            "InvalidIPAddressError was not raised"

    def test__it_inherits_from_base_data(self):
        assert issubclass(HostData, BaseData)
