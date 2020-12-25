from pathlib import Path

# Workaround for bug https://github.com/Fizzadar/pyinfra/issues/496
from pydantic import BaseModel
from pyinfra_cli import inventory
inventory.ALLOWED_DATA_TYPES = tuple(inventory.ALLOWED_DATA_TYPES + (BaseModel,))

from aircraft.deploys.ubuntu.models.v1beta1 import (
    DhcpData,
    DnsmasqData,
    PxeData,
    TftpData,
)

parent_dir = Path('/opt') / 'relaxdiego.com'

tftp = TftpData(
    ip_address='192.168.222.10',
    root_dir=str(parent_dir / 'tftpboot')
)

dnsmasq = DnsmasqData(
    interface='ens33',
    domain='pxe.lan',
    tftp=tftp,
)

dhcp = DhcpData(
    subnet='192.168.222.0/24',
    ranges=[
        dict(start='192.168.222.200', end='192.168.222.254')
    ],
    router='192.168.222.2',
    dns_servers=[
        '1.1.1.1',
        '8.8.8.8',
        '192.168.86.1',
    ],
    tftp_server=tftp.ip_address,
)

pxe = PxeData(
    tftp_root_dir=tftp.root_dir,
    http_root_dir=parent_dir / 'http',
    http_server=tftp.ip_address,

    os_image_source_url='https://releases.ubuntu.com/20.04.1/ubuntu-20.04.1-live-server-amd64.iso',  # NOQA
    os_image_sha256sum='443511f6bf12402c12503733059269a2e10dec602916c0a75263e5d990f6bb93',  # NOQA
    # TODO: Compute this from the filename part of os_image_source_url
    os_image_filename='ubuntu-20.04.1-live-server-amd64.iso',

    grub_image_source_url='http://archive.ubuntu.com/ubuntu/dists/focal/main/uefi/grub2-amd64/current/grubnetx64.efi.signed',  # NOQA
    grub_image_sha256sum='279a5a755bc248d22799434a261b92698740ab817d8aeccbd0cb7409959a1463',  # NOQA

    machines=[
        dict(
            hostname='machine-1',
            ethernets=[
                dict(
                    name='ens33',
                    mac_address='f4:4d:30:63:1c:41',
                    final_ip='192.168.222.11/24',
                    nameservers=dhcp.dns_servers,
                    gateway=dhcp.router,
                ),
            ],
        ),
        dict(
            hostname='machine-2',
            ethernets=[
                dict(
                    name='ens33',
                    mac_address='f4:4d:30:63:56:21',
                    final_ip='192.168.222.12/24',
                    nameservers=dhcp.dns_servers,
                    gateway=dhcp.router,
                ),
            ],
        ),
    ],
)
