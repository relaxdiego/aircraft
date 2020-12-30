from ipaddress import (
    AddressValueError,
    IPv4Interface,
)
from urllib.parse import urlparse


# ==========
# EXCEPTIONS
# ==========

class InvalidIPAddressError(ValueError):

    def __init__(self, ip_address):
        msg = f"'{ip_address}' must use CIDR notation."
        super().__init__(msg)


class StringIsNotAUrlError(ValueError):

    def __init__(self, url):
        msg = f"'{url}' is not a valid URL."
        super().__init__(msg)


class UnsupportedSchemaVersion(ValueError):

    def __init__(self, data_obj, supported_schema_versions):
        msg = f"{str(type(data_obj))} is not supported. Supported schemas are " \
              f"{supported_schema_versions}"
        super().__init__(msg)


# ==========
# VALIDATORS
# ==========

def validate_cidr_notation(ip_address):
    try:
        IPv4Interface(ip_address)
    except AddressValueError:
        raise InvalidIPAddressError(ip_address)


def validate_schema_version(data, supported_schema_versions):
    if type(data) not in supported_schema_versions:
        raise UnsupportedSchemaVersion(
            data,
            supported_schema_versions
        )


def validate_url(url):
    result = urlparse(url)
    if result.scheme == '' and result.netloc == '':
        raise StringIsNotAUrlError(url)
