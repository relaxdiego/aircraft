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
        msg = f"Group '{group}' contains members that are unknown: " \
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
    infra_vms: Optional[List[str]]
    ip_address: Optional[str]

    @validator('ip_address')
    def must_be_a_valid_ip_address(cls, ip_address):
        validate_ip_address(ip_address)
        return ip_address


class Host(BaseModel):
    data: HostData = HostData()


class GroupData(BaseData):
    pass


class Group(BaseModel):
    data: GroupData = GroupData()
    members: Optional[List[str]]


class Inventory(BaseModel):
    hosts: Dict[str, Host]
    groups: Dict[str, Group]

    @validator('groups')
    def groups_members_must_be_known_hosts(cls, groups, values):
        # If validation already failed from a previous field, then 'hosts'
        # will not have been set. In that case, skip this validation.
        if 'hosts' not in values:
            return groups

        hosts = values['hosts'].keys()

        for group, spec in groups.items():
            if group == 'all' and spec.members is not None:
                raise AllGroupDefinesMembersError(spec.members)
            elif spec.members is None:
                raise GroupHasNoMembersError(group)

            unknown_hosts = [host for host in spec.members
                             if host not in hosts]
            if len(unknown_hosts) > 0:
                raise UnknownGroupMembersError(group, unknown_hosts)

        return groups

    @validator('groups')
    def ensure_all_group_is_defined(cls, groups, values):
        if 'all' not in groups.keys():
            groups['all'] = Group()

        return groups

    class Config:
        allow_mutation = False
