from ipaddress import (
    IPv4Address,
)
from pydantic import (
    BaseModel,
    Schema,
)


class MachineData(BaseModel):
    schema_version: str = Schema('v1beta1', const=True)
    model_name: str = Schema('MachineData', const=True)

    hostname: str
    mac_address: str
    provisioning_ip: IPv4Address
    static_ip: IPv4Address

    class Config:
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'
