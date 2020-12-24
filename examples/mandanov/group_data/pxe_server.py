# Workaround for bug https://github.com/Fizzadar/pyinfra/issues/496
from pydantic import BaseModel
from pyinfra_cli import inventory
inventory.ALLOWED_DATA_TYPES = tuple(inventory.ALLOWED_DATA_TYPES + (BaseModel,))

from aircraft.deploys.ubuntu.models.v1beta1 import (
    DnsmasqData,
)

dnsmasq = DnsmasqData(
    interface='eno1',
    domain='pxe.lan',
    dhcp=dict(
        subnet='192.168.100.0/24',
        ranges=[
            dict(start='192.168.100.200', end='192.168.100.254')
        ],
        router='192.168.100.1',
        dns_servers=[
            '192.168.86.1',
            '1.1.1.1',
            '8.8.8.8',
        ]
    ),
    tftp=dict(
        root_path='/opt/relaxdiego.com/tftpboot',
    ),
)
