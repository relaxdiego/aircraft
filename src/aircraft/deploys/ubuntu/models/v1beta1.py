from pathlib import Path

from ipaddress import (
    IPv4Address,
    IPv4Network,
)
from pydantic import (
    BaseModel,
    Schema,
    validator,
)
from typing import (
    List,
    Optional,
)


class V1Beta1BaseModel(BaseModel):
    schema_version: str = Schema('v1beta1', const=True)

    class Config:
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'


class DhcpRangeData(V1Beta1BaseModel):
    start: IPv4Address
    end: IPv4Address

    @validator('end')
    def end_must_be_more_than_start(cls, end, values):
        start = values['start']
        if not start <= end:
            raise ValueError(f"DHCP range {start} > {end} is invalid. "
                             "Start address must be less than or equal to end address.")
        return end


class DhcpData(V1Beta1BaseModel):
    subnet: IPv4Network
    ranges: List[DhcpRangeData]
    router: IPv4Address
    dns_servers: List[IPv4Address]

    @validator('ranges')
    def range_must_be_within_subnet(cls, ranges, values):
        subnet = values['subnet']
        for r in ranges:
            if r.start not in subnet.hosts() or r.end not in subnet.hosts():
                valid_hosts = subnet.hosts()
                first = next(valid_hosts)
                for last in valid_hosts:
                    pass

                raise ValueError(f"DHCP range {r.start} > {r.end} is not within the "
                                 f"subnet {subnet}. Must be within {first} > {last}")
        return ranges


class TftpData(V1Beta1BaseModel):
    root_path: Path

    # Seems like an anti-pattern
    @validator('root_path')
    def coerce_root_path_to_string_after_all_validations(cls, path):
        return str(path)


class DnsmasqData(V1Beta1BaseModel):
    interface: str
    domain: str
    dhcp: Optional[DhcpData]
    tftp: Optional[TftpData]
