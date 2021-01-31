from aircraft.deploys.ubuntu import (
    apache2,
    dnsmasq,
)


# Consumes host.data.dnsmasq
dnsmasq.uninstall()

# Consumes host.data.http
apache2.uninstall()
