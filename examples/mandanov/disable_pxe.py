from aircraft.deploys.ubuntu import (
    isc_dhcp_server,
    tftpd_hpa,
)

isc_dhcp_server.uninstall()
tftpd_hpa.uninstall()
