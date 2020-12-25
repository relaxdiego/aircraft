from pathlib import Path

from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
)
from pydantic import (
    AnyUrl,
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


class TftpData(V1Beta1BaseModel):
    root_dir: Path
    ip_address: IPv4Address

    # Seems like an anti-pattern
    @validator('root_dir')
    def coerce_root_path_to_string_after_all_validations(cls, path):
        return str(path)


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
    tftp_server: IPv4Address

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


class DnsmasqData(V1Beta1BaseModel):
    interface: str
    domain: str
    dhcp: Optional[DhcpData]
    tftp: Optional[TftpData]


class EthernetInterfaceData(V1Beta1BaseModel):
    name: str
    mac_address: str
    final_ip: IPv4Interface
    nameservers: List[IPv4Address]
    gateway: IPv4Address


class MachineData(V1Beta1BaseModel):
    hostname: str
    ethernets: List[EthernetInterfaceData]


class PxeData(V1Beta1BaseModel):
    tftp_root_dir: Path
    http_root_dir: Path
    http_server: IPv4Address

    os_image_source_url: AnyUrl
    os_image_sha256sum: str
    os_image_filename: str

    grub_image_source_url: AnyUrl
    grub_image_sha256sum: str

    machines: List[MachineData]

    # Seems like an anti-pattern
    @validator('http_root_dir')
    def coerce_root_path_to_string_after_all_validations(cls, path):
        return str(path)
