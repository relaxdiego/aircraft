from ipaddress import (
    AddressValueError,
    IPv4Interface,
)
from typing import (
    Dict,
    List,
    Optional,
)
from pydantic import (
    BaseModel,
    validator,
)


def validate_ip_address(ip_address):
    try:
        IPv4Interface(ip_address)
    except AddressValueError:
        raise InvalidIPAddressError(ip_address)
    return ip_address


class InvalidIPAddressError(ValueError):

    def __init__(self, ip_address):
        msg = f"'{ip_address}' is not a valid IP address."
        super().__init__(msg)


class BaseData(BaseModel):
    interface: Optional[str]
    gateway: Optional[str]
    nameservers: Optional[List[str]]

    class Config:
        extra = 'forbid'

    @validator('gateway')
    def gateway_must_be_an_ip_address(cls, ip_address):
        return validate_ip_address(ip_address)

    @validator('nameservers')
    def nameservers_must_be_an_ip_address(cls, nameservers):
        (validate_ip_address(nameserver) for nameserver in nameservers)
        return nameservers


class HostData(BaseData):
    ip_address: Optional[str]

    @validator('ip_address')
    def ip_address_must_be_of_cidr_notation(cls, ip_address):
        return validate_ip_address(ip_address)


class HostSpec(BaseModel):
    data: HostData


class GroupData(BaseData):
    pass


class GroupSpec(BaseModel):
    data: GroupData = GroupData()
    hosts: Optional[List[str]]


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
            # Skip this group if it doesnot have a hosts field
            if spec.hosts is None:
                continue

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
