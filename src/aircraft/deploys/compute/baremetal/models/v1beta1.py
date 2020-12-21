from ipaddress import (
    IPv4Address,
)
from pydantic import (
    BaseModel,
    Schema,
    validator,
)


from aircraft.validators import validate_cidr_notation


class MachineData(BaseModel):
    schema_version: str = Schema('v1beta1', const=True)
    model_name: str = Schema('MachineData', const=True)

    hostname: str
    mac_address: str
    provisioning_ip: IPv4Address
    static_ip: str

    class Config:
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'

    @validator('static_ip')
    def must_be_a_cidr_notation(cls, ip_address):
        validate_cidr_notation(ip_address)
        return ip_address
