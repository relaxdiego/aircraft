from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
    files,
    systemd,
)

from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure isc-dhcp-server')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1',
    ]

    validate_schema_version(host.data.dhcp, supported_schema_versions)

    apt.packages(
        name='Install package',
        packages=['isc-dhcp-server'],
        update=True,
        sudo=True,

        state=state, host=host,
    )

    dhcpd_conf = files.template(
        name='Render configuration',
        src=str(deploy_dir / 'templates' / 'isc-dhcp-server.conf.j2'),
        dest=str(Path('/etc') / 'dhcp' / 'dhcpd.conf'),
        mode='744',
        user='root',
        group='root',
        sudo=True,
        dhcp=host.data.dhcp,

        state=state, host=host,
    )

    systemd.service(
        name='Restart service',
        service='isc-dhcp-server',
        running=True,
        restarted=dhcpd_conf.changed,
        sudo=True,

        state=state, host=host,
    )

    # for machine in host.data.pxe.machines:
    #     for ethernet in machine.ethernets:
    #         filename = ethernet.mac_address.lower().replace(':', '-')
    #         files.template(
    #             name=f'Ensure bootloader config for {machine.hostname}',
    #             src=str(deploy_dir / 'templates' / 'pxelinux.cfg.j2'),
    #             dest=str(pxelinux_cfg_dir / filename),
    #             create_remote_dir=True,
    #             machine=machine,
    #             ethernet=ethernet,
    #             sudo=True,
    #
    #             host=host, state=state,
    #         )


@deploy('Uninstall the DHCP server')
def uninstall(state=None, host=None):
    supported_schema_versions = [
        'v1beta1',
    ]

    validate_schema_version(host.data.dhcp, supported_schema_versions)

    systemd.service(
        name='Restart isc-dhcp-server',
        service='isc-dhcp-server',
        running=False,
        sudo=True,

        state=state, host=host,
    )
