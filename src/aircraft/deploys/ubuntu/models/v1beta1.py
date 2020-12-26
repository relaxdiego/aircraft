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
    address: IPv4Address


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
    ip_addresses: List[IPv4Interface]
    nameservers: List[IPv4Address]
    gateway: IPv4Address


class StorageLvmLogicalVolumeConfigData(V1Beta1BaseModel):
    type: str = Schema('lvm_partition', const=True)
    id: str = None
    name: str
    size: int
    preserve: bool = False

    format: str
    mount_path: Path

    @validator('id', pre=True, always=True)
    def ensure_id(cls, value):
        return value or f'lv-{uuid4()}'

    def export(self):
        return self.dict(exclude={'schema_version', 'format', 'mount_path'},
                         exclude_none=True)


class StorageLvmVolGroupConfigData(V1Beta1BaseModel):
    type: str = Schema('lvm_volgroup', const=True)
    id: str = None
    name: str
    devices: List[str]
    preserve: bool = False

    logical_volumes: List[StorageLvmLogicalVolumeConfigData]

    @validator('id', pre=True, always=True)
    def ensure_id(cls, value):
        return value or f'volgroup-{uuid4()}'

    def export(self):
        return self.dict(exclude={'schema_version', 'logical_volumes'})

    def export_logical_volumes(self):
        return [{**logical_volume.export(), **{'volgroup': self.id}}
                for logical_volume in self.logical_volumes]

    def export_formats(self):
        return [{'fstype': logical_volume.format,
                 'volume': logical_volume.id,
                 'preserve': False,
                 'type': 'format',
                 # id is referenced in self.export_mounts()
                 'id': f'filesystem-for-{logical_volume.id}'}
                for logical_volume in self.logical_volumes]

    def export_mounts(self):
        return [{'device': f'filesystem-for-{logical_volume.id}',
                 'path': str(logical_volume.mount_path),
                 'type': 'mount',
                 'id': f'mount-for-{logical_volume.id}'}
                for logical_volume in self.logical_volumes
                if logical_volume.format is not None]


class StoragePartition(V1Beta1BaseModel):
    type: str = Schema('partition', const=True)
    id: str = None
    size: int
    wipe: str = 'superblock'
    flag: str = ''
    preserve: bool = False
    grub_device: Optional[bool]

    format: Optional[str]
    mount_path: Optional[Path]

    @validator('id', pre=True, always=True)
    def ensure_id(cls, value):
        return value or f'partition-{uuid4()}'

    def export(self):
        return self.dict(exclude={'schema_version', 'format', 'mount_path'},
                         exclude_none=True)


class StorageDiskConfigData(V1Beta1BaseModel):
    type: str = Schema('disk', const=True)
    id: str = None
    path: str
    ptable: str = 'gpt'
    wipe: str = 'superblock'
    preserve: bool = False
    name: str = ''
    grub_device: bool = False

    partitions: List[StoragePartition]

    @validator('id', pre=True, always=True)
    def ensure_id(cls, value):
        return value or f'disk-{uuid4()}'

    def export(self):
        return self.dict(exclude={'schema_version', 'partitions'})

    def export_partitions(self):
        return [{**partition.export(), **{'device': self.id, 'number': number}}
                for number, partition in enumerate(self.partitions, start=1)]

    def export_formats(self):
        return [{'fstype': partition.format,
                 'volume': partition.id,
                 'preserve': False,
                 'type': 'format',
                 # id is referenced in self.export_mounts()
                 'id': f'filesystem-for-{partition.id}'}
                for partition in self.partitions
                if partition.format is not None]

    def export_mounts(self):
        return [{'device': f'filesystem-for-{partition.id}',
                 'path': str(partition.mount_path),
                 'type': 'mount',
                 'id': f'mount-for-{partition.id}'}
                for partition in self.partitions
                if partition.format is not None]


class StorageConfigData(V1Beta1BaseModel):
    disks: List[StorageDiskConfigData]
    lvm_volgroups: List[StorageLvmVolGroupConfigData]

    def export_disks(self):
        return [disk.export() for disk in self.disks]

    def export_partitions(self):
        return [partition
                for disk in self.disks
                for partition in disk.export_partitions()]

    def export_formats(self):
        return [fmt
                for disk in self.disks
                for fmt in disk.export_formats()]

    def export_lvm_volgroups(self):
        return [lvm_volgroup.export() for lvm_volgroup in self.lvm_volgroups]

    def export_lvm_logical_volumes(self):
        return [logical_volume
                for lvm_volgroup in self.lvm_volgroups
                for logical_volume in lvm_volgroup.export_logical_volumes()]

    def export_lvm_formats(self):
        return [fmt
                for volgroup in self.lvm_volgroups
                for fmt in volgroup.export_formats()]

    def export_mounts(self):
        return [mount
                for disk in self.disks
                for mount in disk.export_mounts()] + \
               [mount
                for lvm_volgroup in self.lvm_volgroups
                for mount in lvm_volgroup.export_mounts()]


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
