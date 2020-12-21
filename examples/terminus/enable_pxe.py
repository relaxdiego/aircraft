from pyinfra import host

from aircraft.deploys.network.edge_os import dhcp_server
from aircraft.deploys.network.synology import tftp_server

if 'dhcp_server' in host.groups:
    dhcp_server.configure()

if 'tftp_server' in host.groups:
    tftp_server.configure()
