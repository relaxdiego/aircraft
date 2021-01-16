from pathlib import Path
from uuid import uuid4

from pydantic import (
    Field,
    validator,
)
from typing import (
    List,
    Optional,
)

from .base_model import BaseModel


class StorageLvmLogicalVolumeConfigData(BaseModel):
    type: str = Field('lvm_partition', const=True)
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


class StorageLvmVolGroupConfigData(BaseModel):
    type: str = Field('lvm_volgroup', const=True)
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


class StoragePartition(BaseModel):
    type: str = Field('partition', const=True)
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


class StorageDiskConfigData(BaseModel):
    type: str = Field('disk', const=True)
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


class StorageConfigData(BaseModel):
    disks: List[StorageDiskConfigData]
    lvm_volgroups: List[StorageLvmVolGroupConfigData] = []

    def export_disks(self):
        return [disk.export() for disk in self.disks]

    def export_partitions(self):
        return [partition
                for disk in self.disks
                for partition in disk.export_partitions()]

    def export_formats(self):
        return [fmt
                for disk in self.disks
                for fmt in disk.export_formats()] + \
               [fmt
                for volgroup in self.lvm_volgroups
                for fmt in volgroup.export_formats()]

    def export_lvm_volgroups(self):
        return [lvm_volgroup.export() for lvm_volgroup in self.lvm_volgroups]

    def export_lvm_logical_volumes(self):
        return [logical_volume
                for lvm_volgroup in self.lvm_volgroups
                for logical_volume in lvm_volgroup.export_logical_volumes()]

    def export_mounts(self):
        return [mount
                for disk in self.disks
                for mount in disk.export_mounts()] + \
               [mount
                for lvm_volgroup in self.lvm_volgroups
                for mount in lvm_volgroup.export_mounts()]
