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
        # Quasi-immutable model
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'


class TftpData(V1Beta1BaseModel):
    root_dir: Path


class HttpData(V1Beta1BaseModel):
    root_dir: Path


class BootfileData(V1Beta1BaseModel):
    # The PXE client architecture for which this bootfile is for. PXE client
    # architecture values are listd in RFC 4578
    # https://tools.ietf.org/html/rfc4578#section-2.1
    client_arch: int

    image_source_url: AnyUrl
    image_sha256sum: str

    # Where the bootfile should be saved relative to tftp.root_dir. The actual
    # saving will be done by the consumer of the pxe data whereas it will
    # just be referenced by the consumer of the dhcp data via Option 67
    path: Path


class DhcpRangeData(V1Beta1BaseModel):
    start: IPv4Address
    end: IPv4Address
    lease_time: str = '1m'

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
    bootfiles: List[BootfileData]

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
    interfaces: List[str] = []
    dhcp: Optional[DhcpData]
    tftp: Optional[TftpData]


class EthernetInterfaceData(V1Beta1BaseModel):
    name: str
    ip_address: IPv4Interface
    nameservers: List[IPv4Address]
    gateway: IPv4Address


class MachineData(V1Beta1BaseModel):
    hostname: str
    ethernets: List[EthernetInterfaceData]


class PxeData(V1Beta1BaseModel):
    tftp: TftpData
    http: HttpData

    os_image_source_url: AnyUrl
    os_image_sha256sum: str

    bootfiles: List[BootfileData]

    machines: List[MachineData]

    preserve_files_on_uninstall: bool = False
