from ipaddress import (
    AddressValueError,
    IPv4Interface,
)
from pydantic import (
    BaseModel,
    validator,
)
from typing import (
    List,
    Optional,
)

from aircraft.models.types import StringOrLocator


# =======
# HELPERS
# =======

def validate_ip_address(ip_address):
    try:
        IPv4Interface(ip_address)
    except AddressValueError:
        raise InvalidIPAddressError(ip_address)
    return ip_address


# ==========
# EXCEPTIONS
# ==========

class AllGroupDefinesMembersError(ValueError):

    def __init__(self, members):
        msg = f"Group 'all' explicitly declares members: {','.join(members)}"
        super().__init__(msg)


class GroupHasNoMembersError(ValueError):

    def __init__(self, group):
        msg = f"Group '{group}' does not have members"
        super().__init__(msg)


class UnknownGroupMembersError(ValueError):

    def __init__(self, group, unknown_hosts):
        msg = f"Group '{group.name}' contains members that are unknown: " \
              f"{','.join(unknown_hosts)}"
        super().__init__(msg)


class InvalidIPAddressError(ValueError):

    def __init__(self, ip_address):
        msg = f"'{ip_address}' is not a valid IP address."
        super().__init__(msg)


# ======
# MODELS
# ======


class BaseData(BaseModel):
    interface: Optional[StringOrLocator]
    gateway: Optional[StringOrLocator]
    nameservers: Optional[List[StringOrLocator]]

    class Config:
        extra = 'forbid'

    @validator('gateway')
    def gateway_must_be_an_ip_address(cls, ip_address):
        return validate_ip_address(ip_address)

    @validator('nameservers')
    def nameservers_must_be_an_ip_address(cls, nameservers):
        (validate_ip_address(nameserver) for nameserver in nameservers)
        return nameservers


class GuestSpec(BaseModel):
    name: StringOrLocator


class HostData(BaseData):
    guests: Optional[List[GuestSpec]]
    ip_address: Optional[StringOrLocator]

    @validator('ip_address')
    def must_be_a_valid_ip_address(cls, ip_address):
        validate_ip_address(ip_address)
        return ip_address


class HostSpec(BaseModel):
    name: StringOrLocator
    data: HostData = HostData()


class GroupData(BaseData):
    pass


class GroupSpec(BaseModel):
    name: StringOrLocator
    data: GroupData = GroupData()
    members: Optional[List[StringOrLocator]] = []


class InventorySpec(BaseModel):
    hosts: List[HostSpec]
    groups: Optional[List[GroupSpec]] = []

    @validator('groups')
    def groups_members_must_be_known_hosts(cls, groups, values):
        # If validation already failed from a previous field, then 'hosts'
        # will not have been set. In that case, skip this validation.
        if 'hosts' not in values:
            return groups

        defined_host_names = [host.name for host in values['hosts']]

        for group in groups:
            if group.members is None and group.name != 'all':
                raise GroupHasNoMembersError(group)

            unknown_hosts = [member for member in group.members
                             if member not in defined_host_names]
            if len(unknown_hosts) > 0:
                raise UnknownGroupMembersError(group, unknown_hosts)

        return groups

    @validator('groups')
    def ensure_all_group_is_defined(cls, groups, values):
        all_group = next((group for group in groups
                          if group.name == 'all'), None)

        if all_group is None:
            groups.append(GroupSpec(
                name='all',
                members=[host.name for host in values['hosts']]))

        return groups


class Inventory(BaseModel):
    kind: str
    api_version: str
    spec: InventorySpec

    class Config:
        allow_mutation = False
