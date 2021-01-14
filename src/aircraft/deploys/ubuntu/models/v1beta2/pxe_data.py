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


class PxeData(BaseModel):
    tftp: TftpData
    http: HttpData

    os_image_source_url: AnyHttpUrl
    os_image_sha256sum: str

    bootfiles: List[BootfileData]

    machines: List[MachineData]

    preserve_files_on_uninstall: bool = False
