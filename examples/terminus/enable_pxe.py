from pyinfra import host

from aircraft.deploys.network.edge_os import dhcp_server

if 'dhcp_server' in host.groups:
    dhcp_server.configure()
