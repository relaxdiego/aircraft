from textwrap import dedent
import unittest
import yaml
from pydantic.error_wrappers import ValidationError
import pytest

from aircraft.models.deployspec.inventory.hypervisor.kvm.v1beta1 import (
    GroupSpec,
    Inventory,
)


class HypervisorKvmInventoryV1Beta1Test(unittest.TestCase):

    def test__raises_an_error_if_a_group_member_is_unknown(self):
        d = yaml.safe_load(dedent(
            """
            kind: hypervisor.kvm
            api_version: v1beta1
            spec:
              hosts:
              - name: kvm-1
              groups:
              - name: group-1
                members:
                - kvm-1
                - unknown-host
            """))

        with pytest.raises(ValidationError) as excep_info:
            Inventory(**d)

        assert excep_info.value.errors()[0]['type'] \
            == 'value_error.unknowngroupmembers', \
            "UnknownGroupMembersError was not raised"

    def test__ensures_that_all_group_is_always_present(self):
        d = yaml.safe_load(dedent(
            """
            kind: hypervisor.kvm
            api_version: v1beta1
            spec:
              hosts:
              - name: kvm-1
              groups:
              - name: group-1
                members:
                - kvm-1
            """))

        inventory = Inventory(**d)

        all_group = next((group for group in inventory.spec.groups
                          if group.name == 'all'), None)
        assert type(all_group) == GroupSpec, "Group 'all' was not found"
