from aircraft.deploys.network.edge_os.models.v1beta1 import DhcpData

ssh_user = 'ubnt'
ssh_password = 'ubnt'

dhcp = DhcpData(
    shared_network_name='pxe.lan',
    subnet='192.168.100.0/24',
    start='192.168.100.200',
    stop='192.168.100.254',
    default_router='192.168.100.1',
    dns_server='192.168.86.1',
    bootfile_server='192.168.86.43',
).dict()
