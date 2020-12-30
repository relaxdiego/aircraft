from pyinfra import host

from aircraft.deploys.ubuntu import dnsmasq
from aircraft.deploys.synology import pxe

if 'dhcp_server' in host.groups:
    dnsmasq.configure()

if 'pxe_server' in host.groups:
    pxe.configure()
