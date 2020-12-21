from pathlib import Path

from ipaddress import (
    IPv4Address,
)
from pydantic import (
    AnyUrl,
    BaseModel,
    Schema,
)


class TftpData(BaseModel):
    schema_version: str = Schema('v1beta1', const=True)
    model_name: str = Schema('TftpData', const=True)

    address: IPv4Address
    ssh_rootdir: Path
    sftp_rootdir: Path
    image_base_url: AnyUrl
    image_filename: str

    class Config:
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'
