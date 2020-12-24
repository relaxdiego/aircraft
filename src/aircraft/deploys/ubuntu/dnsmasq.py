from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
    files,
    systemd,
)

from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure dnsmasq')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1',
    ]

    validate_schema_version(host.data.dnsmasq, supported_schema_versions)

    apt.packages(
        name='Install dnsmasq',
        packages=['dnsmasq'],
        update=True,
        sudo=True,

        state=state, host=host,
    )

    if host.data.dnsmasq.tftp is not None:
        files.directory(
            name=f'Ensure TFTP root dir {host.data.dnsmasq.tftp.root_path}',
            path=host.data.dnsmasq.tftp.root_path,
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

# @deploy('Disable DHCP server')
# def disable(state=None, host=None):
#     supported_schema_versions = [
#         'v1beta1'
#     ]
#
#     validate_schema_version(host.data.dhcp, supported_schema_versions)
#
#     filename = f"{host.data.dhcp.schema_version}/dhcp-disable.sh.j2"
#     file_path = './dhcp-disable.sh'
#
#     files.template(
#         name='Render configuration script',
#         src=deploy_dir / 'templates' / filename,
#         dest=file_path,
#         mode='700',
#         state=state, host=host,
#     )
#
#     server.shell(
#         name="Execute configuration script",
#         commands=[
#             file_path
#         ],
#         state=state, host=host,
#     )
