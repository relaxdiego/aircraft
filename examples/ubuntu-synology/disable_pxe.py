from pyinfra import host

from aircraft.deploys.ubuntu import dnsmasq

if 'dhcp_server' in host.groups:
    dnsmasq.uninstall()
