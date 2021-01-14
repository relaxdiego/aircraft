from pathlib import Path

from pyinfra.api import (
    deploy,
)
from pyinfra.operations import (
    files,
    server,
)

from aircraft.deploys.synology.models import v1beta2
from aircraft.validators import validate_schema_version

# This is bad. Each deploy dir should be independent. I'm just
# too lazy to copy the templates and files right now because it
# would mean modifying two copies at the same time. Some fix is
# needed down the road.
deploy_dir = Path(__file__).parent.parent / 'ubuntu'


@deploy('Configure the PXE server')
def configure(state=None, host=None):
    supported_schema_versions = [
        v1beta2.PxeData,
    ]

    validate_schema_version(host.data.pxe, supported_schema_versions)

    templates_base = deploy_dir / 'templates'
    # Make sure to strip any trailing / in os_image_source_url.path
    # otherwise the whole thing will resolve into an absolute path
    # starting only with os_image_source_url.path.
    downloaded_iso_ssh_path = \
        host.data.pxe.http.root_dir / host.data.pxe.os_image_source_url.path.lstrip('/')

    files.directory(
        name='Ensure OS image directory',
        path=str(host.data.pxe.http.root_dir),
        present=True,

        host=host, state=state,
    )

    os_image = files.download(
        name='Download OS image',
        src=str(host.data.pxe.os_image_source_url),
        dest=str(downloaded_iso_ssh_path),
        sha256sum=host.data.pxe.os_image_sha256sum,
        sudo=True,

        host=host, state=state,
    )

    kernel_path = str(host.data.pxe.tftp.root_dir / 'vmlinuz')
    initrd_path = str(host.data.pxe.tftp.root_dir / 'initrd')

    if host.fact.file(kernel_path) is None or \
       host.fact.file(initrd_path) is None or \
       os_image.changed:
        server.shell(
            name='Mount the ISO to /mnt',
            commands=[
                f'mount | grep "{downloaded_iso_ssh_path} on /mnt" || '
                f'mount {downloaded_iso_ssh_path} /mnt',
            ],
            sudo=True,

            host=host, state=state
        )

        server.shell(
            name="Extract kernel and ramdisk image from ISO",
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

    for bootfile in host.data.pxe.bootfiles:

        bootfile_ssh_dir = (host.data.pxe.tftp.root_dir / bootfile.get_path()).parent

        files.directory(
            name='Ensure bootfile directory',
            path=str(bootfile_ssh_dir),
            present=True,

            host=host, state=state,
        )

        files.download(
            name=f'Download bootfile {bootfile.image_source_url}',
            src=str(bootfile.image_source_url),
            dest=str(host.data.pxe.tftp.root_dir / bootfile.get_path()),
            sha256sum=bootfile.image_sha256sum,

            host=host, state=state,
        )

    # Synology's SFTP permissions are unusual in that they don't allow
    # you to create directories (which we want to do in the files.template
    # operation after this one). As a workaround to that, we're going to
    # ensure the directory via the files.directory operation since it uses
    # just SSH.
    files.directory(
        name='Ensure grub/ directory exists',
        path=str(host.data.pxe.tftp.root_dir / 'grub'),
        present=True,

        host=host, state=state,
    )

    files.template(
        name='Render GRUB config',
        src=str(templates_base / 'grub.cfg.j2'),
        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
        dest=str(host.data.pxe.tftp.sftp_root_dir / 'grub' / 'grub.cfg'),
        create_remote_dir=False,
        pxe=host.data.pxe,
        os_name=str(Path(host.data.pxe.os_image_source_url.path).name),

        host=host, state=state,
    )

    for machine in host.data.pxe.machines:

        machine_ssh_root = host.data.pxe.http.root_dir / machine.hostname
        machine_sftp_root = host.data.pxe.http.sftp_root_dir / machine.hostname

        # Synology's SFTP permissions are unusual in that they don't allow
        # you to create directories (which we want to do in the files.template
        # operations after this one). As a workaround to that, we're going to
        # ensure the directory via the files.directory operation since it uses
        # just SSH.
        files.directory(
            name=f"Ensure {machine_ssh_root} exists",
            path=str(machine_ssh_root),
            present=True,

            host=host, state=state,
        )

        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
        meta_data_path = machine_sftp_root / 'meta-data'
        files.template(
            name=f'Render {meta_data_path}',
            src=str(deploy_dir / 'templates' / 'meta-data.j2'),
            dest=str(meta_data_path),
            create_remote_dir=False,
            machine=machine,

            host=host, state=state,
        )

        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
        user_data_path = machine_sftp_root / 'user-data'
        files.template(
            name=f'Render {user_data_path}',
            src=str(deploy_dir / 'templates' / 'user-data.j2'),
            dest=str(user_data_path),
            create_remote_dir=False,
            machine=machine,

            host=host, state=state,
        )
