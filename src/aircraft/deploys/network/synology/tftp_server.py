from pathlib import Path

from pyinfra.api import (
    deploy,
)
from pyinfra.operations import (
    files,
)

from aircraft.validators import validate_schema_version


@deploy('Configure the TFTP server')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1'
    ]

    validate_schema_version(host.data.tftp, supported_schema_versions)

    src = Path(__file__).parent / 'templates' / 'grub.cfg.j2'
    dest = host.data.tftp['sftp_rootdir'] / 'grub' / 'grub.cfg'

    files.template(
        src=str(src),
        dest=str(dest),
        create_remote_dir=False,
        host=host, state=state,
    )
