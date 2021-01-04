from pathlib import Path
from uuid import uuid4

from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
)
from pydantic import (
    AnyUrl,
    AnyHttpUrl,
    BaseModel,
    Field,
    validator,
)
from typing import (
    List,
    Optional,
)


class V1Beta1BaseModel(BaseModel):
    class Config:
        # Quasi-immutable model
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'




class BootfileData(V1Beta1BaseModel):
    """
    Contains information on a bootfile (such as grub) as well as which
    PXE client architecture it applies to. For more information on PXE
    client architectures, see https://tools.ietf.org/html/rfc4578#section-2.1
    """
    client_arch: int
    image_source_url: AnyUrl
    image_sha256sum: str

    def get_path(self):
        """
        Returns the path to the file. This may be used by TFTP packaged
        deploy to determine where to save the file as well as by the
        DHCP packaged deploy to determine what value to provide in
        DHCP Option 67 (Bootfile-Name)
        """
        return self.image_source_url.path.lstrip('/')


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
    tftp_server_name: Optional[IPv4Address]

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


class DnsData(V1Beta1BaseModel):
    """
    TODO: Implement me
    """
    pass


class DnsmasqData(V1Beta1BaseModel):
    """
    Contains information on which interfaces dnsmasq should listen to for client
    requests. Note that all fields are optional. If the interfaces field is not
    assigned, then it will be assumed that dnsmasq should listen on all interfaces.
    Likewise if dhcp is not assigned, then it is assumed that dnsmasq should not
    serve DHCP requests.
    """
    interfaces: List[str] = []
    dns: Optional[DnsData]
    dhcp: Optional[DhcpData]
    tftp: Optional[TftpData]


class EthernetInterfaceData(V1Beta1BaseModel):
    name: str
    ip_addresses: List[IPv4Interface]
    nameservers: List[IPv4Address]
    gateway: IPv4Address


class MachineData(V1Beta1BaseModel):
    hostname: str
    storage: StorageConfigData
    ethernets: List[EthernetInterfaceData]


class PxeData(V1Beta1BaseModel):
    tftp: TftpData
    http: HttpData

    os_image_source_url: AnyHttpUrl
    os_image_sha256sum: str

    bootfiles: List[BootfileData]

    machines: List[MachineData]

    preserve_files_on_uninstall: bool = False
