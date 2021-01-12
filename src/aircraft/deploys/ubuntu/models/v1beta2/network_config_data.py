from ipaddress import (
    IPv4Address,
    IPv4Interface,
)
from pydantic import (
    Field,
    validator,
)
import textwrap
from typing import (
    List,
)
import yaml


from .base_model import BaseModel


class AddressesList(list):
    """
    Custom field for a list of IP addresses. Use this to automatically
    validate if your list contains only valid IP addresses. Example:

        from pydantic import BaseModel

        class MyNetworkConfiguration(BaseModel):
            addresses: AddressesList

        # This should raise a ValueError on the second item in the provided list
        MyNetworkConfiguration({addresses: ['1.2.4.4', 'abcd']})
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.ensure_addresses_are_valid_ips

    @classmethod
    def ensure_addresses_are_valid_ips(cls, addresses):
        for addr in addresses:
            try:
                IPv4Address(addr)
            except ValueError as e:
                raise ValueError(f"{addr} is not a valid IP address") from e
        return addresses


class CidrAddressesList(list):
    """
    Custom field for a list of IP addresses. Use this to automatically
    validate if your list contains only valid IP addresses in CIDR notation.
    Example:

        from pydantic import BaseModel

        class MyNetworkConfiguration(BaseModel):
            addresses: CidrAddressesList

        # This should raise a ValueError on the second item in the provided list
        MyNetworkConfiguration({addresses: ['1.2.4.4/24', '1.2.4.4']})
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.ensure_addresses_are_in_cidr_notation

    @classmethod
    def ensure_addresses_are_in_cidr_notation(cls, addresses):
        for addr in addresses:
            try:
                IPv4Interface(addr)
            except ValueError as e:
                raise ValueError(f"{addr} must be in CIDR notation") from e
        return addresses


class NetworkNameServersBaseModel(BaseModel):
    addresses: AddressesList


class NetworkDeviceBaseModel(BaseModel):
    addresses: CidrAddressesList = None
    dhcp4: bool
    gateway4: str = None
    nameservers: NetworkNameServersBaseModel = None
    mtu: int = None

    @validator('gateway4')
    def ensure_gateway_is_ip_address(cls, value):
        try:
            IPv4Address(value)
        except ValueError as e:
            raise ValueError(f"{value} is not a valid IP address") from e
        return value


class NetworkBondConfigParametersData(BaseModel):
    mode: str
    lacp_rate: str = Field(alias='lacp-rate')
    mii_monitor_interval: int = Field(alias='mii-monitor-interval')


class NetworkVlanConfigData(NetworkDeviceBaseModel):
    id: int


class NetworkBondConfigData(BaseModel):
    name: str
    dhcp4: bool
    interfaces: List[str]
    parameters: NetworkBondConfigParametersData
    vlans: List[NetworkVlanConfigData] = []


class NetworkBridgeParametersData(BaseModel):
    forward_delay: int = Field(alias='forward-delay')
    priority: int
    stp: bool


class NetworkBridgeConfigData(NetworkDeviceBaseModel):
    interfaces: List[str]
    name: str
    parameters: NetworkBridgeParametersData


class NetworkEthernetConfigData(BaseModel):
    name: str
    dhcp4: bool
    vlans: List[NetworkVlanConfigData] = []


class NetworkConfigData(BaseModel):
    """
    Used for declaratively defining the network configuration of a machine.
    This model allows you to, for example, directly declare a VLAN within a
    network device such as a bond or an ethernet interface, reducing duplicate
    data and reducing errors. Example:

        network_config = NetworkConfigData({
            ethernets=[
                {
                    'name': 'eno1',
                    'dhcp4': False,
                },
                {
                    'name': 'eno2',
                    'dhcp4': False,
                }
            ],
            bonds=[
                {
                    'name': 'bond0',
                    'dhcp4': False,
                    'interfaces': [
                        'eno1',
                        'eno2'
                    ]
                    'vlans': [
                        {
                            'id': 147,
                            'dhcp4': False,
                            'addresses': [
                                '192.168.93.132/24'
                            ]
                        }
                    ],
                    'parameters': {
                        'mode': 'active-backup',
                        'primary': 'enp3s0',
                    }
                }
            ],
            bridges=[
                {
                    'name': 'br0',
                    'addresses': [
                        '192.168.94.100/24',
                    ],
                    interfaces=[
                        'bond0',
                    ]
                }
            ]
        })

        # Optionally output to a netplan v2 config:
        netplan = network_config.export_netplan_v2()
    """
    ethernets: List[NetworkEthernetConfigData] = []
    bonds: List[NetworkBondConfigData] = []
    bridges: List[NetworkBridgeConfigData] = []

    # TODO: Move to NetworkBondConfigData as export_netplan_v2()
    def export_bonds(self):
        return {
            'bonds': {
                bond.name: bond.dict(by_alias=True, exclude={'name', 'vlans'})
                for bond in self.bonds
            },
        }

    # TODO: Move to NetworkBridgeConfigData as export_netplan_v2()
    def export_bridges(self):
        return {
            'bridges': {
                bridge.name: bridge.dict(by_alias=True,
                                         exclude={'name'},
                                         exclude_none=True)
                for bridge in self.bridges
            }
        }

    # TODO: Move to NetworkEthernetConfigData as export_netplan_v2()
    def export_ethernets(self):
        return {
            'ethernets': {
                ethernet.name: {
                    'dhcp4': ethernet.dhcp4
                }
                for ethernet in self.ethernets
            },
        }

    def export_netplan_v2(self, format='yaml', indent=0):
        netplan_dict = {
            'network': {
                'version': 2,
                'renderer': 'networkd',
                **self.export_ethernets(),
                **self.export_bonds(),
                **self.export_vlans(),
                **self.export_bridges(),
            }
        }

        return textwrap.indent(yaml.dump(netplan_dict), " " * indent)

    # TODO: Distribute across the various models it calls and (maybe)
    #       make it a part of their export_netplan_v2() methods.
    def export_vlans(self):
        return {
            'vlans': {
                **{
                    f"{device.name}.{vlan.id}": {
                        **vlan.dict(exclude_none=True),
                        'link': device.name,
                    }
                    for device in self.ethernets
                    for vlan in device.vlans
                },
                **{
                    f"{device.name}.{vlan.id}": {
                        **vlan.dict(exclude_none=True),
                        'link': device.name,
                    }
                    for device in self.bonds
                    for vlan in device.vlans
                },
            }
        }
