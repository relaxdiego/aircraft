import unittest

from aircraft.models.deployment.inventory.hypervisor.kvm.v1beta1 import (
    BaseData,
    GroupData,
)


class GroupDataTest(unittest.TestCase):

    def test__it_inherits_from_base_data(self):
        assert issubclass(GroupData, BaseData)
