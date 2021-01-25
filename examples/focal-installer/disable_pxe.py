from pyinfra import (
    host,
)

from aircraft.deploys.ubuntu import (
    apache2,
    dnsmasq,
)


if 'dhcp_server' in host.groups:
    # Consumes host.data.dnsmasq
    dnsmasq.uninstall()

    # Consumes host.data.http
    apache2.uninstall()
