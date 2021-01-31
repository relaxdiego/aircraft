from pyinfra.operations import (
    apt,
)

from aircraft.deploys import (
    ubuntu,
)


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

# Consumes host.data.pxe
ubuntu.pxe.configure()
