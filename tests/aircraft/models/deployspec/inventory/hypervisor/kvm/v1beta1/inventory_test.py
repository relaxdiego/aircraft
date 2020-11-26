import unittest
from pydantic.error_wrappers import ValidationError
import pytest

from aircraft.models.deployment.inventory.hypervisor.kvm.v1beta1 import (
    Group,
    Inventory,
)


class InventoryTest(unittest.TestCase):

    def test__raises_an_error_if_a_group_member_is_unknown(self):
        d = {
            'hosts': {
                'kvm-1': {}
            },
            'groups': {
                'group-a': {
                    'members': [
                        'kvm-1',
                        'unknown-host',
                    ]
                }
            }
        }

        with pytest.raises(ValidationError):
            Inventory(**d)

    def test__ensures_that_all_group_is_always_present(self):
        d = {
            'hosts': {},
            'groups': {},
        }

        inventory = Inventory(**d)

        assert type(inventory.groups['all']) == Group
