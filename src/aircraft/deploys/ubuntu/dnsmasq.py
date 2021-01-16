from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
    files,
    systemd,
)

from aircraft.deploys.ubuntu.models import v1beta3
from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure dnsmasq')
def configure(state=None, host=None):
    supported_schemas = [
        v1beta3.DnsmasqData
    ]

    validate_schema_version(host.data.dnsmasq, supported_schemas)

    apt.packages(
        name='Install dnsmasq',
        packages=['dnsmasq'],
        sudo=True,

        state=state, host=host,
    )

    if host.data.dnsmasq.tftp is not None:
        files.directory(
            name=f'Ensure TFTP root dir {host.data.dnsmasq.tftp.root_dir}',
            path=str(host.data.dnsmasq.tftp.root_dir),
            present=True,
            recursive=True,
            sudo=True,

            state=state, host=host,
        )

    dnsmasq_conf = files.template(
        name='Render the dnsmasq config',
        src=str(deploy_dir / 'templates' / 'dnsmasq.conf.j2'),
        dest=str(Path('/etc') / 'dnsmasq.conf'),
        mode='744',
        user='root',
        group='root',
        sudo=True,
        dnsmasq=host.data.dnsmasq,

        state=state, host=host,
    )

    systemd.service(
        name='Restart dnsmasq',
        service='dnsmasq',
        running=True,
        restarted=dnsmasq_conf.changed,
        sudo=True,

        state=state, host=host,
    )


@deploy('Uninstall dnsmasq')
def uninstall(state=None, host=None):
    supported_schemas = [
        v1beta3.DnsmasqData
    ]

    validate_schema_version(host.data.dnsmasq, supported_schemas)

    if 'dnsmasq.service' in host.fact.systemd_status:
        systemd.service(
            name='Stop dnsmasq',
            service='dnsmasq',
            running=False,
            sudo=True,

            state=state, host=host,
        )

    files.file(
        name='Remove dnsmasq config',
        path=str(Path('/etc') / 'dnsmasq.conf'),
        present=False,
        sudo=True,

        state=state, host=host,
    )

    if host.data.dnsmasq.tftp is not None:
        files.directory(
            name=f'Remove TFTP root dir {host.data.dnsmasq.tftp.root_dir}',
            path=str(host.data.dnsmasq.tftp.root_dir),
            present=False,
            recursive=False,
            sudo=True,

            state=state, host=host,
        )

    apt.packages(
        name='Ensure dnsmasq package is not present',
        packages=['dnsmasq'],
        present=False,
        sudo=True,

        state=state, host=host,
    )
