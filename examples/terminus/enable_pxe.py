from pyinfra import host

from aircraft.deploys.network.edge_os import dhcp_server
from aircraft.deploys.network.synology import pxe_server

if 'dhcp_server' in host.groups:
    dhcp_server.configure()

if 'pxe_server' in host.groups:
    pxe_server.configure()
