from pathlib import Path

from aircraft.deploys.compute.baremetal.models.v1beta1 import MachineData
from aircraft.deploys.network.edge_os.models.v1beta1 import DhcpData
from aircraft.deploys.network.synology.models.v1beta1 import PxeData


machines = [
    MachineData(
        hostname='kvm-01',
        mac_address='f4:4d:30:63:1c:41',
        provisioning_ip='192.168.100.201',
        static_ip='192.168.100.11/24',
    ),
    MachineData(
        hostname='kvm-02',
        mac_address='f4:4d:30:63:56:21',
        provisioning_ip='192.168.100.202',
        static_ip='192.168.100.12/24',
    ),
]

pxe = PxeData(
    ssh_rootdir=Path('/') / 'volume4' / 'pxe',
    # Certain pyinfra file operations use SFTP to transfer files so we
    # have to use a different base path in the case of Synology which
    # presents a different filesystem hierarchy depending on which protocol
    # you're on.
    # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
    sftp_rootdir=Path('/') / 'pxe',

    tftp_address='192.168.100.3',
    http_base_url='http://192.168.100.3:8080',

    os_image_source_url='https://releases.ubuntu.com/20.04.1/ubuntu-20.04.1-live-server-amd64.iso',  # NOQA
    os_image_sha256sum='443511f6bf12402c12503733059269a2e10dec602916c0a75263e5d990f6bb93',  # NOQA
    os_image_filename='ubuntu-20.04.1-live-server-amd64.iso',

    grub_image_source_url='http://archive.ubuntu.com/ubuntu/dists/focal/main/uefi/grub2-amd64/current/grubnetx64.efi.signed',  # NOQA
    grub_image_sha256sum='279a5a755bc248d22799434a261b92698740ab817d8aeccbd0cb7409959a1463',  # NOQA

    machines=machines,
).dict()  # BUG https://github.com/Fizzadar/pyinfra/issues/496

dhcp = DhcpData(
    shared_network_name='pxe.lan',
    subnet='192.168.100.0/24',
    start='192.168.100.200',
    stop='192.168.100.254',
    default_router='192.168.100.1',
    dns_server='192.168.86.1',
    bootfile_server=pxe['tftp_address'],
    machines=machines,
).dict()  # BUG https://github.com/Fizzadar/pyinfra/issues/496
