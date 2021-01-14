from pyinfra.operations import (
    apt,
)

from aircraft.deploys.ubuntu import (
    apache2,
    dnsmasq,
    pxe,
)

apt.update(
    name="Update apt cache",
    cache_time=2592000,  # 30 days
    touch_periodic=True,
    sudo=True,
)

# Consumes host.data.dnsmasq
dnsmasq.configure()

# Consumes host.data.http
apache2.configure()

# Consumes host.data.pxe
pxe.configure()
