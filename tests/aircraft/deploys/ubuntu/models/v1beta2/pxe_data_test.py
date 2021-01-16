import pytest

from aircraft.deploys.ubuntu.models.v1beta3 import PxeData
from aircraft.deploys.ubuntu.models.v1beta3.pxe_data import InstallerConfigData


@pytest.fixture
def valid_bootfiles_config_data():
    return [
        {
            'client_arch': 7,
            'image_source_url': 'http://some.domain.com/some/path/to/file.efi',
            'image_sha256sum': '0123456789abcdef',
        }
    ]


@pytest.fixture
def valid_tftp_config_data():
    return {
        'hostname': '192.168.100.1',
        'root_dir': '/some/path/to/some/dir',
    }


@pytest.fixture
def valid_http_config_data():
    return {
        'hostname': '192.168.100.1',
        'root_dir': '/some/path/to/some/dir',
    }


@pytest.fixture
def valid_with_autoinstall_v1_installer(
    valid_bootfiles_config_data,
    valid_http_config_data,
    valid_tftp_config_data,
):
    return {
        'tftp': valid_tftp_config_data,
        'http': valid_http_config_data,

        'bootfiles': valid_bootfiles_config_data,

        'installer': {
            'type': 'autoinstall-v1',
            'image_source_url': 'http://some.domain.com/some/path/to/file.iso',
            'image_sha256sum': '0123456789abcdef',
        }
    }


# TODO: Add more tests
def test__raises_a_value_error_when_tftp_is_not_provided():
    with pytest.raises(ValueError):
        PxeData()


def test__recognizes_an_installer_dict(valid_with_autoinstall_v1_installer):
    assert isinstance(PxeData(**valid_with_autoinstall_v1_installer).installer,
                      InstallerConfigData)
