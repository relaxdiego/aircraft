# Standard Library imports go here
import unittest
from unittest.mock import (
    call,
    create_autospec,
    patch,
)
from uuid import uuid4

# Operator Frmework imports go here
from ops.testing import Harness

# Imports of your charm's objects go here
from src.charm import (
    ChangeMeCharm,
    ImageMeta,
    on_start_handler,
    _build_juju_pod_spec_dict,
)


# Helper function used for mocking in the tests below
def a_function(*args, **kwargs):
    pass


# Actual tests

class ChangeMeCharmTest(unittest.TestCase):

    def setUp(self):
        self.harness = Harness(ChangeMeCharm)

    def test__init__runs_succesfully(self):
        # Setup
        harness = self.harness

        # Exercise
        harness.begin()

        # Assert
        # No assertions needed for this test

    @patch('src.charm.on_start_handler', spec_set=True, autospec=True)
    def test__on_start_delegator__calls_on_start_handler(self, mock_handler):
        # Setup
        harness = self.harness
        harness.disable_hooks()
        harness.add_oci_resource('changeme-image')
        harness.begin()

        # Exercise
        harness.charm.on.start.emit()

        # Assert
        assert mock_handler.call_count == 1


class OnStartHandlerTest(unittest.TestCase):

    def test_it_does_not_run_if_it_is_not_the_leader(self):
        # Setup
        mock_model_name = str(uuid4())
        mock_app_name = str(uuid4())
        mock_unit_name = str(uuid4())
        mock_image_meta = ImageMeta(registrypath=str(uuid4()),
                                    username=str(uuid4()),
                                    password=str(uuid4()))
        mock_set_pod_spec_func = create_autospec(a_function)
        mock_set_unit_status_func = create_autospec(a_function)

        # Exercise
        on_start_handler(
            model_name=mock_model_name,
            app_name=mock_app_name,
            unit_name=mock_unit_name,
            unit_is_leader=False,
            image_meta=mock_image_meta,
            set_pod_spec_func=mock_set_pod_spec_func,
            set_unit_status_func=mock_set_unit_status_func
        )

        # Assert
        assert mock_set_pod_spec_func.call_count == 0
        assert mock_set_unit_status_func.call_count == 0

    @patch('src.charm._build_juju_pod_spec_dict', autospec=True, spec_set=True)
    @patch('src.charm.MaintenanceStatus', autospec=True, spec_set=True)
    def test_it_sets_the_pod_spec_and_unit_status_if_it_is_leader(
            self,
            mock_maintenance_status_cls,
            mock_build_juju_pod_spec_dict_func):
        # Setup
        mock_model_name = str(uuid4())
        mock_app_name = str(uuid4())
        mock_unit_name = str(uuid4())
        mock_image_meta = ImageMeta(registrypath=str(uuid4()),
                                    username=str(uuid4()),
                                    password=str(uuid4()))
        mock_set_pod_spec_func = create_autospec(a_function)
        mock_set_unit_status_func = create_autospec(a_function)
        mock_maintenance_status = mock_maintenance_status_cls.return_value

        # Exercise
        on_start_handler(
            model_name=mock_model_name,
            app_name=mock_app_name,
            unit_name=mock_unit_name,
            unit_is_leader=True,
            image_meta=mock_image_meta,
            set_pod_spec_func=mock_set_pod_spec_func,
            set_unit_status_func=mock_set_unit_status_func
        )

        # Assert
        assert mock_set_pod_spec_func.call_count == 1
        assert mock_set_pod_spec_func.call_args == \
            call(mock_build_juju_pod_spec_dict_func.return_value)

        assert mock_set_unit_status_func.call_count == 1
        assert mock_set_unit_status_func.call_args == \
            call(mock_maintenance_status)


class BuildJujuPodSpecDictTest(unittest.TestCase):

    def test_it_returns_a_well_formed_container_spec_inside(self):
        # Setup
        mock_app_name = str(uuid4())
        mock_image_meta = ImageMeta(registrypath=str(uuid4()),
                                    username=str(uuid4()),
                                    password=str(uuid4()))

        # Exercise
        output_dict = _build_juju_pod_spec_dict(mock_app_name, mock_image_meta)

        # Assert
        assert isinstance(output_dict, dict)
        assert output_dict == {
            'containers': [{
                'name': mock_app_name,
                'imageDetails': {
                    'imagePath': mock_image_meta.registrypath,
                    'username': mock_image_meta.username,
                    'password': mock_image_meta.password
                },
                'ports': [{
                    'containerPort': 3000,
                    'protocol': 'TCP'
                }],
                'readinessProbe': {
                    'httpGet': {
                        'path': '/api/health',
                        'port': 3000
                    },
                    'initialDelaySeconds': 10,
                    'timeoutSeconds': 30
                }
            }]
        }
