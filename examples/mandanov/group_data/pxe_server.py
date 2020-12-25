from pathlib import Path

# Workaround for bug https://github.com/Fizzadar/pyinfra/issues/496
from pydantic import BaseModel
from pyinfra_cli import inventory
inventory.ALLOWED_DATA_TYPES = tuple(inventory.ALLOWED_DATA_TYPES + (BaseModel,))

from aircraft.deploys.ubuntu.models.v1beta1 import (
    DhcpData,
    PxeData,
    TftpData,
)

parent_dir = Path('/opt') / 'relaxdiego.com'

tftp = TftpData(
    ip_address='192.168.100.11',
    root_dir=str(parent_dir / 'tftpboot')
)

dhcp = DhcpData(
    subnet='192.168.100.0/24',
    ranges=[
        dict(start='192.168.100.200', end='192.168.100.254')
    ],
    router='192.168.100.1',
    dns_servers=[
        '1.1.1.1',
        '8.8.8.8',
        '192.168.86.1',
    ],
    tftp_server=tftp.ip_address,
)

pxe = PxeData(
    tftp_root_dir=tftp.root_dir,
    http_root_dir=str(parent_dir / 'http'),
    machines=[
        dict(
            hostname='kvm-01',
            ethernets=[
                dict(
                    name='eno1',
                    mac_address='f4:4d:30:63:1c:41',
                    final_ip='192.168.100.11/24',
                    nameservers=dhcp.dns_servers,
                    gateway=dhcp.router,
                ),
            ],
        ),
        dict(
            hostname='kvm-02',
            ethernets=[
                dict(
                    name='eno1',
                    mac_address='f4:4d:30:63:56:21',
                    final_ip='192.168.100.12/24',
                    nameservers=dhcp.dns_servers,
                    gateway=dhcp.router,
                ),
            ],
        ),
    ],
)
