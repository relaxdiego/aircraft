import unittest
from unittest.mock import (
    call,
    patch,
)
from uuid import uuid4

from aircraft.models.deployspec import inventory


class LoadTest(unittest.TestCase):

    @patch('aircraft.models.deployspec.inventory.import_module',
           autospec=True, spec_set=True)
    def test__it_loads_the_correct_model(self,
                                         mock_import_module_func):
        # Prep
        inventory_dict = {
            'kind': f'kind_{uuid4()}.{uuid4()}',
            'api_version': f'version_v{uuid4()}',
            'spec': {}
        }
        mock_module = mock_import_module_func.return_value
        mock_model = mock_module.Inventory.return_value

        # Exercise
        returned_model = inventory.load(inventory_dict)

        # Assert
        assert mock_import_module_func.call_count == 1
        assert mock_import_module_func.call_args == call(
            "aircraft.models.deployspec.inventory."
            f"{inventory_dict['kind']}.{inventory_dict['api_version']}"
        )
        assert mock_module.Inventory.call_count == 1
        assert mock_module.Inventory.call_args == call(**inventory_dict)
        assert returned_model == mock_model
