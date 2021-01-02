from pyinfra import host

from aircraft.deploys.edge_os import dhcp
from aircraft.deploys.synology import pxe

if 'dhcp_server' in host.groups:
    dhcp.configure()

if 'pxe_server' in host.groups:
    pxe.configure()
