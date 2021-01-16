import pytest

from aircraft.deploys.ubuntu.models.v1beta3 import StorageConfigData


@pytest.fixture
def input_config(request):
    marker = request.node.get_closest_marker('data_kwargs')
    config = dict(
        disks=[
            {
                'path': '/dev/sda',
                'partitions': [
                    {
                        'size': 536870912,  # 512MB
                        'format': 'fat32',
                        'mount_path': '/boot/efi',
                        'flag': 'boot',
                        'grub_device': True,
                    },
                    {
                        'size': 1073741824,  # 1GB
                        'format': 'ext4',
                        'mount_path': '/boot',
                    },
                    {
                        'id': 'partition-for-ubuntu-vg',
                        'size': 429496729600,  # 400GB
                    },
                ],
            },
        ],
        lvm_volgroups=[
            {
                'name': 'ubuntu-vg',
                'devices': [
                    'partition-for-ubuntu-vg'
                ],
                'logical_volumes': marker.kwargs.get(
                    'logical_volumes',
                    [
                        {
                            'name': 'ubuntu-lv',
                            'size': 397284474880,  # 370GB
                            'format': 'ext4',
                            'mount_path': '/',
                        }
                    ]
                )
            }
        ]
    )

    return config


@pytest.fixture
def no_lvm_volgroups(request):
    config = dict(
        disks=[
            {
                'path': '/dev/sda',
                'partitions': [
                    {
                        'size': 536870912,  # 512MB
                        'format': 'fat32',
                        'mount_path': '/boot/efi',
                        'flag': 'boot',
                        'grub_device': True,
                    },
                    {
                        'size': 1073741824,  # 1GB
                        'format': 'ext4',
                        'mount_path': '/boot',
                    },
                    {
                        'id': 'partition-for-ubuntu-vg',
                        'size': 429496729600,  # 400GB
                    },
                ],
            },
        ],
    )

    return config


@pytest.mark.data_kwargs(logical_volumes=[])
def test__does_not_error_out_when_lvm_lvs_are_empty(input_config):
    assert StorageConfigData(**input_config).export_lvm_logical_volumes() == []


def test__does_not_error_out_when_lvm_volgroups_is_empty(no_lvm_volgroups):
    assert StorageConfigData(**no_lvm_volgroups).export_lvm_logical_volumes() == []
