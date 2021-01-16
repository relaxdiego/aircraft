from enum import Enum
from pydantic import (
    AnyHttpUrl,
)
from typing import (
    List,
)

from .base_model import BaseModel
from .bootfile_data import BootfileData
from .machine_data import MachineData
from .tftp_data import TftpData
from .http_data import HttpData


class InstallerTypeEnum(str, Enum):
    autoinstall_v1 = 'autoinstall-v1'
    legacy_netboot = 'legacy-netboot'


class InstallerConfigData(BaseModel):
    type: InstallerTypeEnum
    image_source_url: AnyHttpUrl
    image_sha256sum: str


class PxeData(BaseModel):
    tftp: TftpData
    http: HttpData

    bootfiles: List[BootfileData]
    installer: InstallerConfigData

    machines: List[MachineData] = []

    preserve_files_on_uninstall: bool = False
