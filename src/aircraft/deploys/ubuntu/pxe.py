from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
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

    for bootfile in host.data.pxe.bootfiles:
        files.download(
            name=f'Download bootfile {bootfile.path}',
            src=str(bootfile.image_source_url),
            dest=str(host.data.pxe.tftp.root_dir / bootfile.path),
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

    # files.directory(
    #     name=f"Ensure {host.data.pxe.http_base_url}/user-data/ exists",
    #     path=str(host.data.pxe.ssh_rootdir / 'user-data'),
    #     present=True,
    #
    #     host=host, state=state,
    # )
    #
    # files.put(
    #     name='Ensure user-data/index.php',
    #     src=str(files_base / 'user-data' / 'index.php'),
    #     # files.put uses SFTP to transfer files so we have to use
    #     # a different base path in the case of Synology which presents a
    #     # different filesystem hierarchy depending on which protocol you're on.
    #     # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
    #     dest=str(host.data.pxe.sftp_rootdir / 'user-data' / 'index.php'),
    #     create_remote_dir=False,
    #
    #     host=host, state=state,
    # )
    #
    # files.put(
    #     name='Ensure meta-data file',
    #     src=str(files_base / 'meta-data'),
    #     # files.put uses SFTP to transfer files so we have to use
    #     # a different base path in the case of Synology which presents a
    #     # different filesystem hierarchy depending on which protocol you're on.
    #     # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
    #     dest=str(host.data.pxe.sftp_rootdir / 'meta-data'),
    #     create_remote_dir=False,
    #
    #     host=host, state=state,
    # )
    #
    # for machine in host.data.machines:
    #     user_data_dir = host.data.pxe.sftp_rootdir / 'user-data'
    #     files.template(
    #         name=f'Add user-data for {machine.hostname}',
    #         src=str(templates_base / 'user-data.j2'),
    #         # files.template uses SFTP to transfer files so we have to use
    #         # a different base path in the case of Synology which presents a
    #         # different filesystem hierarchy depending on which protocol you're on.
    #         # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
    #         dest=str(user_data_dir / str(machine.provisioning_ip)),
    #         create_remote_dir=False,
    #         machine=machine,
    #
    #         host=host, state=state,
    #     )

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
