from pathlib import Path

# Workaround for bug https://github.com/Fizzadar/pyinfra/issues/496
from pydantic import BaseModel
from pyinfra_cli import inventory
inventory.ALLOWED_DATA_TYPES = tuple(inventory.ALLOWED_DATA_TYPES + (BaseModel,))

from aircraft.deploys.ubuntu.models.v1beta1 import (
    BootfileData,
    DhcpData,
    DnsmasqData,
    HttpData,
    PxeData,
    StorageConfigData,
    TftpData,
)

pxe_server_address = '192.168.222.10'

# Directory in the remote host where PXE-related files
# are going to be created
parent_dir = Path('/opt') / 'relaxdiego.com'

tftp = TftpData(
    root_dir=parent_dir / 'tftpboot',
)

http = HttpData(
    root_dir=parent_dir / 'http',
    address=pxe_server_address
)

bootfiles = [
    BootfileData(
        # The PXE client architecture for which this bootfile is for. PXE client
        # architecture values are listd in RFC 4578
        # https://tools.ietf.org/html/rfc4578#section-2.1
        client_arch=7,  # EFI byte code https://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface#Device_drivers  # NOQA

        image_source_url='http://archive.ubuntu.com/ubuntu/dists/focal/main/uefi/grub2-amd64/current/grubnetx64.efi.signed',  # NOQA
        image_sha256sum='279a5a755bc248d22799434a261b92698740ab817d8aeccbd0cb7409959a1463',  # NOQA

        # Where the bootfile should be saved relative to tftp.root_dir. The actual
        # saving will be done by the consumer of the pxe data whereas it will
        # just be referenced by the consumer of the dhcp data via Option 67
        path='grubx64.efi',
    ),
]

dhcp = DhcpData(
    subnet='192.168.222.0/24',
    ranges=[
        # The pool of IP addresses that will be used during machine
        # provisioning, before they are assigned their static IP
        # addresses during installation.
        dict(start='192.168.222.200', end='192.168.222.254')
    ],
    router='192.168.222.2',
    dns_servers=[
        '1.1.1.1',
        '8.8.8.8',
        '192.168.86.1',
    ],
    bootfiles=bootfiles,
)

dnsmasq = DnsmasqData(
    dhcp=dhcp,
    tftp=tftp,
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
                    # "id" is optional but we're giving this partition one so that
                    # we can reference it in the lvm_volgroup below.
                    'id': 'partition-for-ubuntu-vg',
                    'size': 19327352832,  # 18GB
                    # We're not mounting and formatting it here since we're going
                    # to create an LVM volgroup out of this partition below.
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
                    # TIP: Don't just copy and paste the partition's size from above
                    #      since the volume group also needs some of the partition's
                    #      space for metadata. In the future, we can add an an 'extents'
                    #      option (same arguments as lvcreate's --extents aka -l arg)
                    #      which will be mutually exclusive with 'size'.
                    'size': 10737418240,  # 10GB
                    'format': 'ext4',
                    'mount_path': '/',
                }
            ]
        }
    ]
)

import devtools; devtools.debug(storage_config)  # NOQA: E702, E501

pxe = PxeData(
    tftp=tftp,
    http=http,

    os_image_source_url='https://releases.ubuntu.com/20.04.1/ubuntu-20.04.1-live-server-amd64.iso',  # NOQA
    os_image_sha256sum='443511f6bf12402c12503733059269a2e10dec602916c0a75263e5d990f6bb93',  # NOQA

    bootfiles=bootfiles,

    machines=[
        dict(
            hostname='machine-1',
            storage=storage_config,
            ethernets=[
                dict(
                    name='ens33',
                    ip_addresses=['192.168.100.11/24'],
                    nameservers=dhcp.dns_servers,
                    gateway=dhcp.router,
                ),
            ],
        ),
        dict(
            hostname='machine-2',
            storage=storage_config,
            ethernets=[
                dict(
                    name='ens33',
                    ip_addresses=['192.168.100.12/24'],
                    nameservers=dhcp.dns_servers,
                    gateway=dhcp.router,
                ),
            ],
        ),
    ],

    preserve_files_on_uninstall=True,
)
