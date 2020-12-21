from ipaddress import (
    AddressValueError,
    IPv4Interface,
)


# ==========
# EXCEPTIONS
# ==========

class InvalidIPAddressError(ValueError):

    def __init__(self, ip_address):
        msg = f"'{ip_address}' must use CIDR notation."
        super().__init__(msg)


class UnsupportedSchemaVersion(ValueError):

    def __init__(self, data_obj, supported_schema_versions):
        msg = f"{data_obj['model_name']} {data_obj['schema_version']} " \
              "is not supported. Supported schema versions are " \
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
    return ip_address


def validate_schema_version(data, supported_schema_versions):
    if data['schema_version'] not in supported_schema_versions:
        raise UnsupportedSchemaVersion(
            data,
            supported_schema_versions
        )
