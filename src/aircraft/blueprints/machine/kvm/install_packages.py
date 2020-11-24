from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
)


@deploy('Install KVM', data_defaults={})
def main(state, host):

    apt.packages(
        name='Install required packages',
        packages=[
            'qemu-kvm',
            'libvirt-daemon-system',
            'virtinst'
        ],
        sudo=True,
        update=True,
        cache_time=2592000,  # 30 days

        host=host,
        state=state,
    )
