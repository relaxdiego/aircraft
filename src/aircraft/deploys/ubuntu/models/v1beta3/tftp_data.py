from ipaddress import (
    IPv4Address,
)
from pathlib import Path
from pydantic import (
    validator,
)
from typing import (
    Optional,
)


from .base_model import BaseModel


class TftpData(BaseModel):
    """
    Holds information about where to reach the TFTP server as well as
    the path in the server where the root directory is located. The
    optional sftp_root_dir is available for systems where the SFTP
    subsystem of the SSH service presents a different path. Example
    systems that do this is Synology's DSM. If sftp_root_dir is not
    provided, then it is assumed to have the same value as root_dir.
    """
    hostname: IPv4Address
    root_dir: Path
    sftp_root_dir: Optional[Path]

    @validator('sftp_root_dir', pre=True, always=True)
    def ensure_sftp_root_dir_has_a_value(cls, value, values):
        return value or values['root_dir']
