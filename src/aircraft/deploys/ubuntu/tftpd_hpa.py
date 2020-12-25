from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
    files,
    server,
    systemd,
)

from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure tftpd-hpa')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1',
    ]

    validate_schema_version(host.data.tftp, supported_schema_versions)

    apt.packages(
        name='Install package',
        packages=['tftpd-hpa'],
        update=True,
        sudo=True,

        state=state, host=host,
    )

    files.directory(
        name=f'Ensure directory {host.data.tftp.root_dir}',
        path=str(host.data.tftp.root_dir),
        present=True,
        recursive=True,
        sudo=True,

        state=state, host=host,
    )

    tftpd_conf = files.template(
        name='Render the tftpd config',
        src=str(deploy_dir / 'templates' / 'tftpd-hpa.conf.j2'),
        dest=str(Path('/etc') / 'default' / 'tftpd-hpa'),
        sudo=True,
        tftp=host.data.tftp,

        state=state, host=host,
    )

    systemd.service(
        name='Restart tftp-hpa service',
        service='tftpd-hpa',
        running=True,
        daemon_reload=True,
        restarted=tftpd_conf.changed,
        sudo=True,

        state=state, host=host,
    )
