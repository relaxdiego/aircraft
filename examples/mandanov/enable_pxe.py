from aircraft.deploys.ubuntu import (
    # apache2,
    isc_dhcp_server,
    tftpd_hpa,
    pxe,
)

# apache2.configure()
isc_dhcp_server.configure()
tftpd_hpa.configure()
pxe.configure()
