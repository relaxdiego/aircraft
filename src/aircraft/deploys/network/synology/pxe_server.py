from pathlib import Path

from pyinfra.api import (
    deploy,
)
from pyinfra.operations import (
    files,
)

from aircraft.validators import validate_schema_version


@deploy('Configure the PXE server')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1'
    ]

    validate_schema_version(host.data.pxe, supported_schema_versions)

    local_base_path = Path(__file__).parent / 'templates' / \
        host.data.pxe['schema_version']
    remote_base_path = host.data.pxe['sftp_rootdir']

    files.template(
        src=str(local_base_path / 'grub.cfg.j2'),
        dest=str(remote_base_path / 'grub' / 'grub.cfg'),
        create_remote_dir=False,
        host=host, state=state,
    )

    files.template(
        src=str(local_base_path / 'user-data.j2'),
        dest=str(remote_base_path / 'user-data'),
        create_remote_dir=False,
        host=host, state=state,
    )
