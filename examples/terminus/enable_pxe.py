from pyinfra import host

from aircraft.deploys.ubuntu import dnsmasq
# from aircraft.deploys.network.synology import (
#     tftp_server,
#     http_server,
# )

if 'dhcp_server' in host.groups:
    dnsmasq.configure()
