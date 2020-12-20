from ipaddress import (
    AddressValueError,
    IPv4Address,
    IPv4Interface,
)
from pydantic import (
    BaseModel,
    Schema,
    validator,
)


# =======
# HELPERS
# =======

def validate_cidr_notation(ip_address):
    try:
        IPv4Interface(ip_address)
    except AddressValueError:
        raise InvalidIPAddressError(ip_address)
    return ip_address


# ==========
# EXCEPTIONS
# ==========

class InvalidIPAddressError(ValueError):

    def __init__(self, ip_address):
        msg = f"'{ip_address}' must use CIDR notation."
        super().__init__(msg)


class DhcpData(BaseModel):
    schema_version: str = Schema('v1beta1', const=True)
    model_name: str = Schema('DhcpData', const=True)

    shared_network_name: str
    subnet: str
    start: IPv4Address
    stop: IPv4Address
    default_router: IPv4Address
    dns_server: IPv4Address
    bootfile_server: IPv4Address
    subnet_parameters: str = 'filename &quot;/pxe-boot/pxelinux.0&quot;;'
    bootfile_name: str = '/pxe-boot/pxelinux.0'

    class Config:
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'

    @validator('subnet')
    def must_be_a_cidr_notation(cls, ip_address):
        validate_cidr_notation(ip_address)
        return ip_address
