import unittest
from uuid import uuid4

from pydantic.error_wrappers import ValidationError
import pytest

from aircraft.models.deployment.inventory.hypervisor.kvm.v1beta1 import (
    BaseData,
    HostData,
)


class HostDataTest(unittest.TestCase):

    def test__accepts_a_list_of_infra_vm_names(self):
        infra_vms = [str(uuid4()) for _ in range(4)]
        data = HostData(infra_vms=infra_vms)

        assert data.infra_vms == infra_vms

    def test__raises_an_error_if_ip_address_is_invalid(self):
        with pytest.raises(ValidationError):
            HostData(ip_address=str(uuid4()))

    def test__it_inherits_from_base_data(self):
        assert issubclass(HostData, BaseData)
