from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)

from aircraft.deploys.ubuntu.models import v1beta2
from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure PXE files')
def configure(state=None, host=None):
    supported_schema_versions = [
        v1beta2.PxeData,
    ]

    validate_schema_version(host.data.pxe, supported_schema_versions)

    #
    # Download bootfile(s) and rener grubg.cfg
    #

    for bootfile in host.data.pxe.bootfiles:
        bootfile_dir = (host.data.pxe.tftp.root_dir / bootfile.get_path()).parent

        files.directory(
            name='Ensure bootfile directory',
            path=str(bootfile_dir),
            present=True,
            sudo=True,

            host=host, state=state,
        )

        files.download(
            name=f'Download bootfile {bootfile.get_path()}',
            src=str(bootfile.image_source_url),
            dest=str(host.data.pxe.tftp.root_dir / bootfile.get_path()),
            sha256sum=bootfile.image_sha256sum,
            sudo=True,

            host=host, state=state,
        )

    files.template(
        name='Render GRUB config',
        src=str(deploy_dir / 'templates' / 'grub.cfg.j2'),
        dest=str(host.data.pxe.tftp.root_dir / 'grub' / 'grub.cfg'),
        pxe=host.data.pxe,
        sudo=True,
        os_name=Path(host.data.pxe.os_image_source_url.path).stem,

        host=host, state=state,
    )

    #
    # Download the OS installer image
    #

    iso_path = \
        host.data.pxe.http.root_dir / host.data.pxe.os_image_source_url.path.lstrip('/')

    files.directory(
        name=f"Ensure {iso_path.parent}",
        path=str(iso_path.parent),
        present=True,
        sudo=True,

        host=host, state=state,
    )

    download_iso = files.download(
        name=f'Download OS Image to {iso_path}',
        src=str(host.data.pxe.os_image_source_url),
        dest=str(iso_path),
        sha256sum=host.data.pxe.os_image_sha256sum,
        sudo=True,

        host=host, state=state,
    )

    #
    # Extract the kernel and ram disk image for use by the bootloader
    #

    kernel_path = str(host.data.pxe.tftp.root_dir / 'vmlinuz')
    initrd_path = str(host.data.pxe.tftp.root_dir / 'initrd')

    if host.fact.file(kernel_path) is None or \
       host.fact.file(initrd_path) is None or \
       download_iso.changed:
        server.shell(
            name='Mount the ISO to /mnt',
            commands=[
                f'mount | grep "{iso_path} on /mnt" || mount {iso_path} /mnt',
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
        name=f'Ensure {iso_path} is unmounted',
        commands=[
            f'(mount | grep "{iso_path} on /mnt" && umount /mnt) || :',
        ],
        sudo=True,

        host=host, state=state
    )

    #
    # Render the machine-specific user-data and meta-data files
    #

    for machine in host.data.pxe.machines:
        meta_data_path = host.data.pxe.http.root_dir / machine.hostname / 'meta-data'
        files.template(
            name=f'Render {meta_data_path}',
            src=str(deploy_dir / 'templates' / 'meta-data.j2'),
            dest=str(meta_data_path),
            create_remote_dir=True,
            sudo=True,
            machine=machine,

            host=host, state=state,
        )

        user_data_path = host.data.pxe.http.root_dir / machine.hostname / 'user-data'
        files.template(
            name=f'Render {user_data_path}',
            src=str(deploy_dir / 'templates' / 'user-data.j2'),
            dest=str(user_data_path),
            create_remote_dir=True,
            sudo=True,
            machine=machine,

            host=host, state=state,
        )

    # TODO: Check if this should be moved to apache2.py and if doing that requires
    #       that pxe.configure be executed prior to apache2.configure
    files.directory(
        name=f"Ensure www-data has read permissions in {host.data.pxe.http.root_dir}",
        path=str(host.data.pxe.http.root_dir),
        user='root',
        group='www-data',
        mode='0755',
        recursive=True,
        sudo=True,

        state=state, host=host,
    )
