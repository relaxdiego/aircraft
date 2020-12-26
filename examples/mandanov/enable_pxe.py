from aircraft.deploys.ubuntu import (
    apache2,
    dnsmasq,
    pxe,
)

# Consumes host.data.dnsmasq
dnsmasq.configure()

# # Consumes host.data.http
# apache2.configure()
#
# # Consumes host.data.pxe
# pxe.configure()
