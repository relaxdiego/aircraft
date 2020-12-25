from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
    files,
    server,
)

from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure PXE server')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1',
    ]

    validate_schema_version(host.data.dnsmasq, supported_schema_versions)

    bootloader_files = apt.packages(
        name='Install bootloader files',
        packages=['syslinux', 'pxelinux'],
        update=True,
        sudo=True,

        state=state, host=host,
    )

    if bootloader_files.changed:
        boot_files = [
            '/usr/lib/PXELINUX/pxelinux.0',
            '/usr/lib/syslinux/modules/bios/ldlinux.c32'
        ]

        server.shell(
            name=f'Copy PXE boot files to {host.data.pxe.tftp_root_dir}',
            commands=[
                f'cp -v {f} {host.data.pxe.tftp_root_dir}/' for f in boot_files
            ],
            sudo=True,

            state=state, host=host,
        )

    pxelinux_cfg_dir = Path(host.data.pxe.tftp_root_dir) / 'pxelinux.cfg'

    for machine in host.data.pxe.machines:
        for ethernet in machine.ethernets:
            filename = ethernet.mac_address.lower().replace(':', '-')
            files.template(
                name=f'Ensure bootloader config for {machine.hostname}',
                src=str(deploy_dir / 'templates' / 'pxelinux.cfg.j2'),
                dest=str(pxelinux_cfg_dir / filename),
                create_remote_dir=True,
                machine=machine,
                ethernet=ethernet,
                sudo=True,

                host=host, state=state,
            )
