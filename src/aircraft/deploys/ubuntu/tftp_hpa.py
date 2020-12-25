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


@deploy('Configure the TFTP server')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1',
    ]

    validate_schema_version(host.data.tftp, supported_schema_versions)

    apt.packages(
        name='Install tftp-hpa',
        packages=['tftp-hpa'],
        update=True,
        sudo=True,

        state=state, host=host,
    )

    server.group(
        name="Ensure tftpd group",
        group="tftpd",
        present=True,
        system=True,
        sudo=True,

        state=state, host=host,
    )

    server.user(
        name="Ensure tftpd user",
        user="tftpd",
        present=True,
        home=None,
        shell=None,
        group="tftpd",
        ensure_home=False,
        system=True,
        sudo=True,

        state=state, host=host,
    )

    tftpd_conf = files.template(
        name='Render the tftpd config',
        src=str(deploy_dir / 'templates' / 'tftpd-hpa.conf.j2'),
        dest=str(Path('/etc') / 'default' / 'tftpd-hpa.conf'),
        mode='744',
        user='tftpd',
        group='tftpd',
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
