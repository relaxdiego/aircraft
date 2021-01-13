import pytest
import textwrap
import yaml

from aircraft.deploys.ubuntu.models.v1beta2 import NetworkConfigData


@pytest.fixture
def valid_config_dict():
    return dict(
        ethernets=[
            {
                'name': 'eno1',
                'dhcp4': False,
            },
            {
                'name': 'eno2',
                'dhcp4': False,
            },
            {
                'name': 'eno3',
                'dhcp4': False,
            },
            {
                'name': 'eno4',
                'dhcp4': False,
            },
        ],
        bonds=[
            {
                'name': 'bond0',
                'dhcp4': False,
                'interfaces': ['eno1', 'eno2'],
                'parameters': {
                    'mode': '802.3ad',
                    'lacp-rate': 'fast',
                    'mii-monitor-interval': 100,
                },
                'vlans': [
                    {
                        'id': 142,
                        'dhcp4': False,
                    },
                    {
                        'id': 143,
                        'dhcp4': False,
                    },
                ]
            },
            {
                'name': 'bond1',
                'dhcp4': False,
                'interfaces': ['eno3', 'eno4'],
                'parameters': {
                    'mode': '802.3ad',
                    'lacp-rate': 'fast',
                    'mii-monitor-interval': 100,
                },
                'vlans': [
                    {
                        'id': 147,
                        'dhcp4': False,
                        'addresses': [
                            '192.168.93.132/25',
                        ]
                    },
                    {
                        'id': 148,
                        'dhcp4': False,
                        'addresses': [
                            '192.168.122.4/24',
                        ]
                    },
                ]
            },
        ],
        bridges=[
            {
                'name': 'broam',
                'addresses': ['192.168.87.4/24'],
                'interfaces': ['bond0.142'],
                'gateway4': '192.168.87.1',
                'dhcp4': False,
                'mtu': 1500,
                'nameservers': {
                    'addresses': [
                        '192.168.126.164',
                        '10.177.210.210',
                    ],
                },
                'parameters': {
                    'forward-delay': 0,
                    'priority': 0,
                    'stp': False,
                }
            },
            {
                'name': 'brprovisioning',
                'addresses': ['10.217.141.1/24'],
                'interfaces': ['bond0'],
                'dhcp4': False,
                'mtu': 1500,
                'parameters': {
                    'forward-delay': 0,
                    'priority': 0,
                    'stp': False,
                }
            },
            {
                'name': 'brinternal',
                'addresses': ['10.217.143.1/24'],
                'interfaces': ['bond0.143'],
                'dhcp4': False,
                'mtu': 1500,
                'parameters': {
                    'forward-delay': 0,
                    'priority': 0,
                    'stp': False,
                }
            },
        ]
    )


def test__exports_a_valid_netplan_v2_config_for_user_data(valid_config_dict):
    assert NetworkConfigData(**valid_config_dict).export_netplan_v2(indent=2) == \
        textwrap.indent(
            yaml.dump(
                yaml.safe_load("""
                    network:
                      version: 2
                      renderer: networkd
                      ethernets:
                        eno1:
                          dhcp4: no
                        eno2:
                          dhcp4: no
                        eno3:
                          dhcp4: no
                        eno4:
                          dhcp4: no
                      bonds:
                        bond0:
                          dhcp4: no
                          interfaces: [eno1,eno2]
                          parameters:
                            mode: 802.3ad
                            lacp-rate: fast
                            mii-monitor-interval: 100
                        bond1:
                          dhcp4: no
                          interfaces: [eno3,eno4]
                          parameters:
                            mode: 802.3ad
                            lacp-rate: fast
                            mii-monitor-interval: 100
                      vlans:
                        bond0.142:
                          id: 142
                          link: bond0
                          dhcp4: no
                        bond0.143:
                          id: 143
                          link: bond0
                          dhcp4: no
                        bond1.147:
                          id: 147
                          link: bond1
                          addresses: [192.168.93.132/25]
                          dhcp4: no
                        bond1.148:
                          id: 148
                          link: bond1
                          addresses: [192.168.122.4/24]
                          dhcp4: no
                      bridges:
                        broam:
                          addresses: [192.168.87.4/24]
                          interfaces: [bond0.142]
                          gateway4: 192.168.87.1
                          dhcp4: no
                          mtu: 1500
                          nameservers:
                            addresses:
                                - 192.168.126.164
                                - 10.177.210.210
                          parameters:
                            forward-delay: 0
                            priority: 0
                            stp: false
                        brprovisioning:
                          addresses: [10.217.141.1/24]
                          interfaces: [bond0]
                          dhcp4: false
                          mtu: 1500
                          parameters:
                            forward-delay: 0
                            priority: 0
                            stp: false
                        brinternal:
                          addresses: [10.217.143.1/24]
                          interfaces: [bond0.143]
                          dhcp4: false
                          mtu: 1500
                          parameters:
                            forward-delay: 0
                            priority: 0
                            stp: false

                    """)
            ),
            "  "
    )
