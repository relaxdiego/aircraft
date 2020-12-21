from pathlib import Path

from aircraft.deploys.network.edge_os.models.v1beta1 import DhcpData
from aircraft.deploys.network.synology.models.v1beta1 import PxeData


pxe = PxeData(
    address='192.168.100.3',
    ssh_rootdir=Path('/') / 'volume4' / 'tftp' / 'pxe-boot',
    sftp_rootdir=Path('/') / 'tftp' / 'pxe-boot',
    image_base_url='ftp://192.168.86.43/pxe-boot',
    image_filename='ubuntu-20.04.1-live-server-amd64.iso',
).dict()

dhcp = DhcpData(
    shared_network_name='pxe.lan',
    subnet='192.168.100.0/24',
    start='192.168.100.200',
    stop='192.168.100.254',
    default_router='192.168.100.1',
    dns_server='192.168.86.1',
    bootfile_server=pxe['address'],
).dict()
