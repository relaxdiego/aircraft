from pathlib import Path

from ipaddress import (
    IPv4Address,
)
from pydantic import (
    AnyUrl,
    BaseModel,
    Schema,
    validator,
)
from typing import (
    List,
)

from aircraft.deploys.compute.baremetal.models.v1beta1 import MachineData
from aircraft.validators import validate_url


class PxeData(BaseModel):
    schema_version: str = Schema('v1beta1', const=True)
    model_name: str = Schema('PxeData', const=True)

    address: IPv4Address
    ssh_rootdir: Path
    sftp_rootdir: Path

    os_image_source_url: AnyUrl
    os_image_sha256sum: str
    os_image_base_url: AnyUrl
    os_image_filename: str

    grub_image_source_url: AnyUrl
    grub_image_sha256sum: str

    machines: List[MachineData]

    class Config:
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'

    @validator('source_image_url')
    def source_image_url_must_be_valid(cls, url):
        validate_url(url)
        return url
