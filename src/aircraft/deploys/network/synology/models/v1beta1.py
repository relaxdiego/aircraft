from pathlib import Path

from ipaddress import (
    IPv4Address,
)
from pydantic import (
    AnyUrl,
    BaseModel,
    Schema,
)
from typing import (
    List,
)

from aircraft.deploys.compute.baremetal.models.v1beta1 import MachineData


class PxeData(BaseModel):
    schema_version: str = Schema('v1beta1', const=True)

    ssh_rootdir: Path
    # Certain pyinfra file operations use SFTP to transfer files so we
    # have to use a different base path in the case of Synology which
    # presents a different filesystem hierarchy depending on which protocol
    # you're on.
    # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
    sftp_rootdir: Path

    tftp_address: IPv4Address
    http_base_url: AnyUrl

    os_image_source_url: AnyUrl
    os_image_sha256sum: str
    os_image_filename: str

    grub_image_source_url: AnyUrl
    grub_image_sha256sum: str

    machines: List[MachineData]

    class Config:
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'
