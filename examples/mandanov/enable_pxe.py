from aircraft.deploys.ubuntu import (
    isc_dhcp_server,
    tftpd_hpa,
    # pxe,
)

isc_dhcp_server.configure()
tftpd_hpa.configure()
# pxe.configure()
