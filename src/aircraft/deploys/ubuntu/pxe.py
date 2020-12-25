from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
    files,
    server,
)

from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure PXE files')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1',
    ]

    validate_schema_version(host.data.pxe, supported_schema_versions)

    bootloader_files = apt.packages(
        name='Install bootloader files',
        packages=['syslinux', 'pxelinux'],
        update=True,
        sudo=True,

        state=state, host=host,
    )

    if bootloader_files.changed:
        boot_files = [
            '/usr/lib/PXELINUX/lpxelinux.0',
            '/usr/lib/syslinux/modules/efi64/*.c32'
        ]

        server.shell(
            name=f'Copy bootloader files to {host.data.pxe.tftp_root_dir}',
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
                http_server=host.data.pxe.http_server,
                sudo=True,

                host=host, state=state,
            )

    files.directory(
        name=f'Ensure directory {host.data.pxe.http_root_dir} exists',
        path=str(host.data.pxe.http_root_dir),
        present=True,
        sudo=True,

        host=host, state=state,
    )

    downloaded_iso_path = \
        Path(host.data.pxe.http_root_dir) / host.data.pxe.os_image_filename

    download_iso = files.download(
        name='Download OS Image',
        src=str(host.data.pxe.os_image_source_url),
        dest=str(downloaded_iso_path),
        sha256sum=host.data.pxe.os_image_sha256sum,
        sudo=True,

        host=host, state=state,
    )

    kernel_path = str(host.data.pxe.tftp_root_dir / 'vmlinuz')
    initrd_path = str(host.data.pxe.tftp_root_dir / 'initrd')

    if host.fact.file(kernel_path) is None or \
       host.fact.file(initrd_path) is None or \
       download_iso.changed:
        server.shell(
            name='Mount the ISO to /mnt',
            commands=[
                f'mount | grep "{downloaded_iso_path} on /mnt" || '
                f'mount {downloaded_iso_path} /mnt',
            ],
            sudo=True,

            host=host, state=state
        )

        server.shell(
            name="Extract kernel and initrd from ISO",
            commands=[
                f'cp /mnt/casper/vmlinuz {kernel_path}',
                f'cp /mnt/casper/initrd {initrd_path}',
            ],
            sudo=True,

            host=host, state=state,
        )

        server.shell(
            name='Unmount the ISO',
            commands=[
                'umount /mnt',
            ],
            sudo=True,

            host=host, state=state
        )
