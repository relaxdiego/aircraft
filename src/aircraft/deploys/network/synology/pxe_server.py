from pathlib import Path

from pyinfra.api import (
    deploy,
)
from pyinfra.operations import (
    files,
)

from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure the PXE server')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1'
    ]

    validate_schema_version(host.data.pxe, supported_schema_versions)

    templates_base = deploy_dir / 'templates' / host.data.pxe['schema_version']
    files_base = deploy_dir / 'files'

    files.download(
        name='Download OS Image',
        src=str(host.data.pxe['os_image_source_url']),
        dest=str(host.data.pxe['ssh_rootdir'] / host.data.pxe['os_image_filename']),
        sha256sum=host.data.pxe['os_image_sha256sum'],

        host=host, state=state,
    )

    # Mount iso
    # Extract /mnt/casper/vmlinuz
    # Extract /mnt/casper/initrd

    files.download(
        name='Download GRUB image',
        src=str(host.data.pxe['grub_image_source_url']),
        dest=str(host.data.pxe['ssh_rootdir'] / 'pxelinux.0'),
        sha256sum=host.data.pxe['grub_image_sha256sum'],

        host=host, state=state,
    )

    files.template(
        name='Render GRUB config',
        src=str(templates_base / 'grub.cfg.j2'),
        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        dest=str(host.data.pxe['sftp_rootdir'] / 'grub' / 'grub.cfg'),
        create_remote_dir=False,

        host=host, state=state,
    )

    files.directory(
        name=f"Ensure {host.data.pxe['os_image_base_url']}/user-data/ exists",
        path=str(host.data.pxe['ssh_rootdir'] / 'user-data'),
        present=True,

        host=host, state=state,
    )

    files.put(
        name='Ensure user-data/index.php',
        src=str(files_base / 'user-data' / 'index.php'),
        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        dest=str(host.data.pxe['sftp_rootdir'] / 'user-data' / 'index.php'),
        create_remote_dir=False,

        host=host, state=state,
    )

    for machine in host.data.machines:
        user_data_dir = host.data.pxe['sftp_rootdir'] / 'user-data'
        files.template(
            name=f'Add user-data for {machine.hostname}',
            src=str(templates_base / 'user-data.j2'),
            # files.template uses SFTP to transfer files so we have to use
            # a different base path in the case of Synology which presents a
            # different filesystem hierarchy depending on which protocol you're on.
            dest=str(user_data_dir / str(machine.provisioning_ip)),
            create_remote_dir=False,
            machine=machine,

            host=host, state=state,
        )
