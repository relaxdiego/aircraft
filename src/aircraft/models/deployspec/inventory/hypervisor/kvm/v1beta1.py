from ipaddress import (
    AddressValueError,
    IPv4Interface,
)
import os
from pathlib import Path
import privy
from pydantic import (
    BaseModel,
    validator,
)
from typing import (
    List,
    Optional,
)


#
# TODO: Move this custom type and its companion get_secret_key() helper
#       to more appropriate locations. They are objects that will be used
#       acorss different kinds of inventory so place them in a commonly
#       known location. Maybe models/deployspec/inventory/common.py?
#

# Ref: https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types
class StringOrVariableName(str):
    """
    Custom pydantic data type used to accept a key value that may be a
    string literal or it may be a variable name in the form of
    [secrets|variables]/name_of_variable.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.load_if_variable

    @classmethod
    def load_if_variable(cls, value):
        if str(value).startswith(("secrets/", "variables/")):
            base_path = Path(os.environ['AIRCRAFT_DEPLOYSPEC'])
            with open(base_path / value) as variable_fh:
                data = variable_fh.read()

            if str(value).startswith("secrets/"):
                # TODO: We'll need to create CLI commands secret and secret key CRUD
                data = privy.peek(data, get_secret_key())
        else:
            data = str(value)

        return data


def get_secret_key():
    base_path = Path(os.environ['AIRCRAFT_DEPLOYSPEC'])
    with open(base_path / "cluster_id") as cluster_id_fh:
        cluster_id = cluster_id_fh.readline()

    secret_keys_base_path = Path().home() / '.local' / 'aircraft' / 'secret_keys'
    with open(secret_keys_base_path / cluster_id) as secret_key_fh:
        secret_key = secret_key_fh.read()

    return secret_key


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
    interface: Optional[StringOrVariableName]
    gateway: Optional[StringOrVariableName]
    nameservers: Optional[List[StringOrVariableName]]

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
    name: StringOrVariableName


class HostData(BaseData):
    guests: Optional[List[GuestSpec]]
    ip_address: Optional[StringOrVariableName]

    @validator('ip_address')
    def must_be_a_valid_ip_address(cls, ip_address):
        validate_ip_address(ip_address)
        return ip_address


class HostSpec(BaseModel):
    name: StringOrVariableName
    data: HostData = HostData()


class GroupData(BaseData):
    pass


class GroupSpec(BaseModel):
    name: StringOrVariableName
    data: GroupData = GroupData()
    members: Optional[List[StringOrVariableName]] = []


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
