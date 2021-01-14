import pytest
from unittest import TestCase

from aircraft.deploys.ubuntu.models.v1beta2 import PxeData


# TODO: Add more tests
class PxeDataTest(TestCase):

    def test__raises_a_value_error_when_tftp_is_not_provided(self):
        with pytest.raises(ValueError):
            PxeData()
