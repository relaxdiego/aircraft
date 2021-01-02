from pyinfra import host

from aircraft.deploys.edge_os import dhcp

if 'dhcp_server' in host.groups:
    dhcp.delete()
