from aircraft.deploys.ubuntu import (
    dnsmasq,
    isc_dhcp_server,
    # tftpd_hpa,
    pxe,
)

isc_dhcp_server.configure()
# tftpd_hpa.configure()
dnsmasq.configure()
pxe.configure()
