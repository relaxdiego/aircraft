from pathlib import Path

# Workaround for bug https://github.com/Fizzadar/pyinfra/issues/496
from pydantic import BaseModel
from pyinfra_cli import inventory
inventory.ALLOWED_DATA_TYPES = tuple(inventory.ALLOWED_DATA_TYPES + (BaseModel,))

from aircraft.deploys.ubuntu.models.v1beta1 import (
    BootfileData,
    DhcpData,
    DnsmasqData,
    # HttpData,
    # PxeData,
    # StorageConfigData,
    TftpData,
)

tftp = TftpData(
    hostname='192.168.86.43',
    root_dir=Path('/volume') / 'pxe' / 'tftpboot',
    sftp_root_dir=Path('/pxe') / 'tftpboot',
)

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

dhcp = DhcpData(
    subnet='192.168.100.0/24',
    ranges=[
        # The pool of IP addresses that will be used during machine
        # provisioning, before they are assigned their static IP
        # addresses during installation.
        dict(start='192.168.100.200', end='192.168.100.254')
    ],
    # AKA gateway
    router='192.168.100.1',
    dns_servers=[
        '1.1.1.1',
        '8.8.8.8',
        '192.168.86.1',
    ],
    bootfiles=bootfiles,
    tftp_server_name=tftp.hostname,
)

dnsmasq = DnsmasqData(
    interfaces=['eth0'],
    dhcp=dhcp,
)
