from pyinfra import host
from pyinfra.operations import (
    apt,
)

from aircraft.deploys import (
    synology,
    ubuntu,
)


if 'dhcp_server' in host.groups:
    apt.update(
        name="Update apt cache",
        cache_time=2592000,  # 30 days
        touch_periodic=True,
        sudo=True,
    )

    # Consumes host.data.dnsmasq
    ubuntu.dnsmasq.configure()

    # Consumes host.data.http
    ubuntu.apache2.configure()

if 'pxe_server' in host.groups:
    # Consumes host.data.pxe
    synology.pxe.configure()
