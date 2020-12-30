from pathlib import Path

from aircraft.deploys.ubuntu.models.v1beta1 import TftpData as BaseTftpData


class TftpData(BaseTftpData):
    sftp_root_dir: Path
