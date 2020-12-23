from ipaddress import (
    IPv4Address,
)
from pydantic import (
    BaseModel,
    Schema,
    validator,
)
from typing import (
    List,
)

from aircraft.validators import validate_cidr_notation
from aircraft.deploys.compute.baremetal.models.v1beta1 import MachineData


class DhcpData(BaseModel):
    schema_version: str = Schema('v1beta1', const=True)

    shared_network_name: str
    subnet: str
    start: IPv4Address
    stop: IPv4Address
    default_router: IPv4Address
    dns_server: IPv4Address
    bootfile_server: IPv4Address
    subnet_parameters: str = 'filename &quot;/pxelinux.0&quot;;'
    bootfile_name: str = 'pxelinux.0'
    machines: List[MachineData]

    class Config:
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'

    @validator('subnet')
    def must_be_a_cidr_notation(cls, ip_address):
        validate_cidr_notation(ip_address)
        return ip_address
