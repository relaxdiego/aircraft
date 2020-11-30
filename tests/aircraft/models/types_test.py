import privy
from pydantic import BaseModel
import unittest
from unittest.mock import (
    call,
    patch,
)
from uuid import uuid1

from aircraft.models.types import StringOrLocator


class StringOrLocatorTest(unittest.TestCase):

    @patch('aircraft.models.types.get_deployspec_path', autospec=True, spec_set=True)
    def test__it_fetches_a_secret(self, mock_get_deployspec_path):
        expected = str(uuid1())
        password = str(uuid1())
        encrypted = self.encrypt(expected, password)
        secret_path = f"secrets/{uuid1()}"

        class Model(BaseModel):
            field: StringOrLocator

        model = Model(field=secret_path)

        assert model.field == expected, "Secret was not fetched"

    def encrypt(self, data, password):
        return privy.hide(data.encode('utf-8'), password)
