from pathlib import Path

# Workaround for bug https://github.com/Fizzadar/pyinfra/issues/496
from pydantic import BaseModel
from pyinfra_cli import inventory
inventory.ALLOWED_DATA_TYPES = tuple(inventory.ALLOWED_DATA_TYPES + (BaseModel,))

from aircraft.deploys.edge_os.models.v1beta1 import (
    DhcpData,
)
from aircraft.deploys.synology.models.v1beta1 import (
    PxeData,
)
from aircraft.deploys.ubuntu.models.v1beta1 import (
    BootfileData,
    HttpData,
    StorageConfigData,
    TftpData,
)

pxe_server_address = '192.168.86.43'

bootfiles = [
    BootfileData(
        # The PXE client architecture for which this bootfile is for. PXE client
        # architecture values are listd in RFC 4578
        # https://tools.ietf.org/html/rfc4578#section-2.1
        client_arch=7,  # EFI byte code https://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface#Device_drivers  # NOQA: E501
        image_source_url='http://archive.ubuntu.com/ubuntu/dists/focal/main/uefi/grub2-amd64/2.04-1ubuntu26/grubnetx64.efi.signed',  # NOQA: E501
        image_sha256sum='279a5a755bc248d22799434a261b92698740ab817d8aeccbd0cb7409959a1463',  # NOQA: E501
    ),
]

tftp = TftpData(
    hostname=pxe_server_address,
    root_dir=Path('/volume4') / 'pxe' / 'tftpboot',
    sftp_root_dir=Path('/pxe') / 'tftpboot',
)

http = HttpData(
    hostname=pxe_server_address,
    port=8080,
    root_dir=Path('/volume4') / 'pxe' / 'http',
    sftp_root_dir=Path('/pxe') / 'http',
)

dhcp = DhcpData(
    shared_network_name='pxe.lan',
    subnet='192.168.100.0/24',
    ranges=[
        # The pool of IP addresses that will be used during machine
        # provisioning, before they are assigned their static IP
        # addresses during installation.
        dict(start='192.168.100.200', end='192.168.100.254')
    ],
    router='192.168.100.1',
    dns_servers=[
        '1.1.1.1',
        '8.8.8.8',
        '192.168.86.1',
    ],
    bootfiles=bootfiles,
    tftp_server_name=tftp.hostname,
)

storage_config = StorageConfigData(
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
            'logical_volumes': [
                {
                    'name': 'ubuntu-lv',
                    'size': 397284474880,  # 370GB
                    'format': 'ext4',
                    'mount_path': '/',
                }
            ]
        }
    ]
)

pxe = PxeData(
    tftp=tftp,
    http=http,

    os_image_source_url='https://releases.ubuntu.com/20.04.1/ubuntu-20.04.1-live-server-amd64.iso',  # NOQA: E501
    os_image_sha256sum='443511f6bf12402c12503733059269a2e10dec602916c0a75263e5d990f6bb93',  # NOQA: E501

    bootfiles=bootfiles,

    machines=[
        dict(
            hostname='maas-1',
            storage=storage_config,
            ethernets=[
                dict(
                    name='eno1',
                    ip_addresses=['192.168.100.11/24'],
                    nameservers=dhcp.dns_servers,
                    gateway=dhcp.router,
                ),
            ],
        ),
        dict(
            hostname='maas-2',
            storage=storage_config,
            ethernets=[
                dict(
                    name='eno1',
                    ip_addresses=['192.168.100.12/24'],
                    nameservers=dhcp.dns_servers,
                    gateway=dhcp.router,
                ),
            ],
        ),
    ],
)
