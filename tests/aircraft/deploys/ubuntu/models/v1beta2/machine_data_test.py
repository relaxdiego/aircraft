import pytest
from unittest import TestCase

from aircraft.deploys.ubuntu.models.v1beta2 import MachineData


# TODO: Add more tests
class MachineDataTest(TestCase):

    def test__raises_a_value_error_when_hostname_is_not_provided(self):
        with pytest.raises(ValueError):
            MachineData()
