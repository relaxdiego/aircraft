from aircraft.deploys.ubuntu.models.v1beta3 import DhcpData as BaseDhcpData


class DhcpData(BaseDhcpData):
    shared_network_name: str
    subnet_parameters: str = ""
