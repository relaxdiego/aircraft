from ipaddress import (
    AddressValueError,
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


class InvalidIPAddressError(ValueError):

    def __init__(self, ip_address):
        msg = f"'{ip_address}' is not a valid IP address."
        super().__init__(msg)


class HostData(BaseModel):
    ip_address: str

    @validator('ip_address')
    def ip_address_must_be_of_cidr_notation(cls, ip_address):
        try:
            ip_address = IPv4Interface(ip_address)
        except AddressValueError:
            raise InvalidIPAddressError(ip_address)

        return ip_address


class HostSpec(BaseModel):
    data: HostData


class GroupData(BaseModel):
    interface: str = ""
    gateway: IPv4Address = None
    nameservers: List[IPv4Address] = []


class GroupSpec(BaseModel):
    data: GroupData = GroupData()
    hosts: List[str] = []


class UndefinedHostsError(ValueError):

    def __init__(self, group, undefined_hosts):
        msg = f"Group '{group}' is referencing undefined hosts: " \
              f"{','.join(undefined_hosts)}"
        super().__init__(msg)


class InventorySpec(BaseModel):
    hosts: Dict[str, HostSpec]
    groups: Dict[str, GroupSpec]

    @validator('groups')
    def hosts_in_groups_must_be_defined(cls, groups, values):
        # If validation already failed from a previous field, then 'hosts'
        # will not have been set. In that case, skip this validation.
        if 'hosts' not in values:
            return groups

        hosts = values['hosts'].keys()

        for group, spec in groups.items():
            undefined_hosts = [host for host in spec.hosts
                               if host not in hosts]
            if len(undefined_hosts) > 0:
                raise UndefinedHostsError(group, undefined_hosts)

        return groups

    @validator('groups')
    def ensure_all_group_is_defined(cls, groups, values):
        if 'all' not in groups.keys():
            groups['all'] = GroupSpec()

        return groups

    class Config:
        allow_mutation = False
