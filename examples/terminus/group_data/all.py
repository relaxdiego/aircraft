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
    address='192.168.100.3',
    ssh_rootdir=Path('/') / 'volume4' / 'pxe',
    sftp_rootdir=Path('/') / 'pxe',
    image_base_url='http://192.168.100.3:8080',
    image_filename='ubuntu-20.04.1-live-server-amd64.iso',
    machines=machines,
).dict()

dhcp = DhcpData(
    shared_network_name='pxe.lan',
    subnet='192.168.100.0/24',
    start='192.168.100.200',
    stop='192.168.100.254',
    default_router='192.168.100.1',
    dns_server='192.168.86.1',
    bootfile_server=pxe['address'],
    machines=machines,
).dict()
