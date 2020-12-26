from aircraft.deploys.ubuntu import (
    apache2,
    dnsmasq,
    pxe,
)

# Consumes host.data.dnsmasq
dnsmasq.uninstall()

# Consumes host.data.http
apache2.uninstall()

# Consumes host.data.pxe
pxe.uninstall()
