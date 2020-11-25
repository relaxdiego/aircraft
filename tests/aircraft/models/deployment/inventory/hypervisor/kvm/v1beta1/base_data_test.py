import unittest
from uuid import uuid4

from pydantic.error_wrappers import ValidationError
import pytest

from aircraft.models.deployment.inventory.hypervisor.kvm.v1beta1 import (
    BaseData,
)


class BaseDataTest(unittest.TestCase):

    def test__it_does_not_allow_arbitrary_keys(self):
        d = {
            f'arbitrary_{str(uuid4())}': str(uuid4())
        }

        with pytest.raises(ValidationError):
            BaseData(**d)

    def test__raises_an_error_if_gateway_is_invalid(self):
        with pytest.raises(ValidationError):
            BaseData(gateway=str(uuid4()))

    def test__raises_an_error_if_nameservers_has_an_invalid_value(self):
        with pytest.raises(ValidationError):
            BaseData(gateway=['1.1.1.1', str(uuid4())])
