from ipaddress import (
    IPv4Address,
    IPv4Interface,
)
from typing import (
    Dict,
    List,
)
from pydantic import (
    BaseModel,
    validator,
)


class HostData(BaseModel):
    ip_address: IPv4Interface


class HostSpec(BaseModel):
    data: HostData


class GroupData(BaseModel):
    interface: str
    gateway: IPv4Address
    nameservers: List[IPv4Address]


class GroupSpec(BaseModel):
    data: GroupData
    hosts: List[str]


class UndefinedHostsError(ValueError):

    def __init__(self, group, undefined_hosts):
        msg = "Group '{}' is referencing undefined hosts: '{}'"
        super().__init__(msg.format(group, ', '.join(undefined_hosts)))


class Inventory(BaseModel):
    hosts: Dict[str, HostSpec]
    groups: Dict[str, GroupSpec]

    @validator('groups')
    def hosts_in_groups_must_be_defined(cls, groups, values):
        hosts = values['hosts'].keys()

        for group, spec in groups.items():
            undefined_hosts = [host for host in spec.hosts
                               if host not in hosts]
            if len(undefined_hosts) > 0:
                raise UndefinedHostsError(group, undefined_hosts)

        return groups

    class Config:
        allow_mutation = False
