from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)

from aircraft.deploys.ubuntu.models import v1beta3
from aircraft.deploys.ubuntu.models.v1beta3.pxe_data import InstallerType
from aircraft.validators import validate_schema_version

# This is bad. Each deploy dir should be independent. I'm just
# too lazy to copy the templates and files right now because it
# would mean modifying two copies at the same time. Some fix is
# needed down the road.
deploy_dir = Path(__file__).parent.parent / 'ubuntu'


class UnsupportedInstallerTypeError(Exception):

    def __init__(self, installer):
        msg = f"Unsupported installer type '{installer.type}'"
        super().__init__(msg)


@deploy('Configure Synology PXE')
def configure(state=None, host=None):
    supported_schema_versions = [
        v1beta3.PxeData,
    ]

    validate_schema_version(host.data.pxe, supported_schema_versions)

    #
    # Download bootfile(s)
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

    if host.data.pxe.installer.type == InstallerType.autoinstall_v1:
        configure_installer_type_autoinstall_v1(state=state, host=host)
    elif host.data.pxe.installer.type == InstallerType.legacy_netboot:
        configure_installer_type_legacy_netboot(state=state, host=host)
    else:
        raise UnsupportedInstallerTypeError(host.data.pxe.installer)


def configure_installer_type_autoinstall_v1(state=None, host=None):

    #
    # Download the OS installer image
    #

    iso_path = host.data.pxe.http.root_dir.joinpath(
        host.data.pxe.installer.image_source_url.path.lstrip('/')
    )

    files.directory(
        name=f"Ensure {iso_path.parent}",
        path=str(iso_path.parent),
        present=True,
        sudo=True,

        host=host, state=state,
    )

    download_installer = files.download(
        name=f'Download Installer Image to {iso_path}',
        src=str(host.data.pxe.installer.image_source_url),
        dest=str(iso_path),
        sha256sum=host.data.pxe.installer.image_sha256sum,
        sudo=True,

        host=host, state=state,
    )

    # This deploy only supports serving one OS version for now and
    # to ensure that the extracted bootstrap kernel and ramdisk come
    # from the correct ISO, we use this template as one of the signals
    # in the extraction logic further down. Without this, the OS version
    # being served might change but the bootstrap kernel and ramdisk
    # might not.

    # files.template uses SFTP to transfer files so we have to use
    # a different base path in the case of Synology which presents a
    # different filesystem hierarchy depending on which protocol you're on.
    # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
    current_installer_flag = host.data.pxe.tftp.sftp_root_dir / 'current-installer'
    current_installer = files.template(
        name=f'Write {current_installer_flag}',
        src=deploy_dir / 'templates' / 'current-installer.j2',
        dest=current_installer_flag,

        pxe=host.data.pxe,

        host=host, state=state,
    )

    #
    # Extract the kernel and ram disk image for use by the bootloader
    #

    kernel_path = str(host.data.pxe.tftp.root_dir / 'vmlinuz')
    initrd_path = str(host.data.pxe.tftp.root_dir / 'initrd')

    if host.fact.file(kernel_path) is None or \
       host.fact.file(initrd_path) is None or \
       download_installer.changed or \
       current_installer.changed:
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
    # Render GRUB2 config
    #

    # Synology's SFTP permissions are unusual in that they don't allow
    # you to create directories (which we want to do in the files.template
    # operation after this one). As a workaround to that, we're going to
    # ensure the directory via the files.directory operation since it uses
    # just SSH.
    files.directory(
        name='Ensure grub/ directory exists',
        path=str(host.data.pxe.tftp.root_dir / 'grub'),
        present=True,
        sudo=True,

        host=host, state=state,
    )

    files.template(
        name='Render GRUB config',
        src=str(deploy_dir / 'templates' / 'grub2.autoinstall-v1.cfg.j2'),
        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        dest=str(host.data.pxe.tftp.sftp_root_dir / 'grub' / 'grub.cfg'),
        create_remote_dir=False,

        pxe=host.data.pxe,
        os_name=Path(host.data.pxe.installer.image_source_url.path).stem,
        kernel_filename=Path(kernel_path).name,
        initrd_filename=Path(initrd_path).name,

        host=host, state=state,
    )

    #
    # Render the machine-specific user-data and meta-data files
    #

    for machine in host.data.pxe.machines:
        # Synology's SFTP permissions are unusual in that they don't allow
        # you to create directories (which we want to do in the files.template
        # operation after this one). As a workaround to that, we're going to
        # ensure the directory via the files.directory operation since it uses
        # just SSH.
        machine_dir = host.data.pxe.http.root_dir / machine.hostname
        files.directory(
            name=f'Ensure {machine_dir} exists',
            path=machine_dir,
            present=True,

            host=host, state=state,
        )

        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        meta_data_path = \
            host.data.pxe.http.sftp_root_dir / machine.hostname / 'meta-data'
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
        user_data_path = \
            host.data.pxe.http.sftp_root_dir / machine.hostname / 'user-data'
        files.template(
            name=f'Render {user_data_path}',
            src=str(deploy_dir / 'templates' / 'user-data.j2'),
            dest=str(user_data_path),
            create_remote_dir=False,
            machine=machine,

            host=host, state=state,
        )


def configure_installer_type_legacy_netboot(state=None, host=None):
    #
    # Download the netboot archive
    #

    archive_path = host.data.pxe.tftp.root_dir.joinpath(
        host.data.pxe.installer.netboot_source_url.path.lstrip('/')
    )

    files.directory(
        name=f"Ensure {archive_path.parent}",
        path=str(archive_path.parent),
        present=True,
        sudo=True,

        host=host, state=state,
    )

    download_netboot_archive = files.download(
        name=f'Download netboot archive to {archive_path}',
        src=str(host.data.pxe.installer.netboot_source_url),
        dest=str(archive_path),
        sha256sum=host.data.pxe.installer.netboot_sha256sum,
        sudo=True,

        host=host, state=state,
    )

    #
    # Download the OS iso
    #

    iso_path = host.data.pxe.http.root_dir.joinpath(
        host.data.pxe.installer.image_source_url.path.lstrip('/')
    )

    files.directory(
        name=f"Ensure {iso_path.parent}",
        path=str(iso_path.parent),
        present=True,
        sudo=True,

        host=host, state=state,
    )

    server.shell(
        name=f'Ensure nothing is mounted on {iso_path.parent}/mnt',
        commands=[
            f'(mount | grep " on {iso_path.parent}/mnt" && '
            f'umount {iso_path.parent}/mnt) || :',
        ],
        sudo=True,

        host=host, state=state
    )

    download_iso = files.download(
        name=f'Download OS iso to {iso_path}',
        src=str(host.data.pxe.installer.image_source_url),
        dest=str(iso_path),
        sudo=True,

        sha256sum=host.data.pxe.installer.image_sha256sum,

        host=host, state=state,
    )

    iso_mount_path = iso_path.parent / 'mnt'

    server.shell(
        name=f'Mount the ISO to {iso_path.parent}/mnt',
        commands=[
            f'mkdir -p {iso_path.parent}/mnt',
            f'mount {iso_path} {iso_path.parent}/mnt',
        ],
        sudo=True,

        host=host, state=state
    )

    # This deploy only supports serving one OS version for now and
    # to ensure that the extracted bootstrap kernel and ramdisk come
    # from the correct ISO, we use this template as one of the signals
    # in the extraction logic further down. Without this, the OS version
    # being served might change but the bootstrap kernel and ramdisk
    # might not.

    # files.template uses SFTP to transfer files so we have to use
    # a different base path in the case of Synology which presents a
    # different filesystem hierarchy depending on which protocol you're on.
    # Related bug: https://github.com/Fizzadar/pyinfra/issues/499
    current_installer_flag = host.data.pxe.tftp.sftp_root_dir / 'current-installer'
    current_installer = files.template(
        name=f'Write {current_installer_flag}',
        src=deploy_dir / 'templates' / 'current-installer.j2',
        dest=current_installer_flag,

        pxe=host.data.pxe,

        host=host, state=state,
    )

    #
    # Extract the kernel and ram disk image for use by the bootloader
    #

    kernel_path = host.data.pxe.tftp.root_dir / 'linux'
    initrd_path = host.data.pxe.tftp.root_dir / 'initrd.gz'

    if host.fact.file(kernel_path) is None or \
       host.fact.file(initrd_path) is None or \
       download_netboot_archive.changed or \
       download_iso.changed or \
       current_installer.changed:

        # We make use of the kernel and initrd in the netboot archive
        # since the the ones in the 18.04 iso, specifically under the
        # {iso_mount_path}/install directory, fail to work properly.
        kernel_path_in_archive = './ubuntu-installer/amd64/linux'
        initrd_path_in_archive = './ubuntu-installer/amd64/initrd.gz'

        server.shell(
            name='Extract the files from the netboot installer',
            commands=[
                f'tar -zxvf {archive_path} -C {kernel_path.parent} '
                f'--strip-components={kernel_path_in_archive.count("/")} '
                f'{kernel_path_in_archive}',

                f'tar -zxvf {archive_path} -C {initrd_path.parent} '
                f'--strip-components={initrd_path_in_archive.count("/")} '
                f'{initrd_path_in_archive}',
            ],
            sudo=True,

            host=host, state=state
        )

    #
    # Render Legacy Preseed Config
    #

    # files.template uses SFTP to transfer files so we have to use
    # a different base path in the case of Synology which presents a
    # different filesystem hierarchy depending on which protocol you're on.
    legacy_preseed_manual_path = host.data.pxe.http.sftp_root_dir.joinpath(
        'legacy-preseed-manual.seed'
    )
    # files.template uses SFTP to transfer files so we have to use
    # a different base path in the case of Synology which presents a
    # different filesystem hierarchy depending on which protocol you're on.
    legacy_preseed_auto_dir = host.data.pxe.http.sftp_root_dir.joinpath(
        'legacy-preseed-auto'
    )
    net_image_disk_path = iso_mount_path / 'install' / 'filesystem.squashfs'
    net_image_http_path = str(
        Path(
            host.data.pxe.installer.image_source_url.path.lstrip('/')
        ).parent.joinpath('mnt', 'install', 'filesystem.squashfs')
    )

    server.shell(
        name='Check that squashfs file exists',
        commands=[
            f'test -f {net_image_disk_path}',
        ],
        sudo=True,

        host=host, state=state
    )

    files.template(
        name='Render legacy preseed config',
        src=deploy_dir / 'templates' / 'legacy-preseed-manual.seed.j2',
        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        dest=host.data.pxe.http.sftp_root_dir / legacy_preseed_manual_path,
        create_remote_dir=False,

        pxe=host.data.pxe,
        net_image_http_path=net_image_http_path,

        host=host, state=state,
    )

    #
    # Render GRUB2 config
    #

    installer_path = Path(
        host.data.pxe.installer.netboot_source_url.path.lstrip('/')
    )

    # Synology's SFTP permissions are unusual in that they don't allow
    # you to create directories (which we want to do in the files.template
    # operation after this one). As a workaround to that, we're going to
    # ensure the directory via the files.directory operation since it uses
    # just SSH.
    grub_dir = host.data.pxe.tftp.root_dir / 'grub'
    files.directory(
        name=f'Ensure {grub_dir} exists',
        path=grub_dir,
        present=True,

        host=host, state=state,
    )

    files.template(
        name='Render GRUB config',
        src=deploy_dir / 'templates' / 'grub2.legacy-netboot.cfg.j2',
        # files.template uses SFTP to transfer files so we have to use
        # a different base path in the case of Synology which presents a
        # different filesystem hierarchy depending on which protocol you're on.
        dest=host.data.pxe.tftp.sftp_root_dir / 'grub' / 'grub.cfg',
        create_remote_dir=False,

        initrd_filename=Path(initrd_path).name,
        installer_path=installer_path,
        kernel_filename=kernel_path.name,
        legacy_preseed_auto_dir=legacy_preseed_auto_dir.stem,
        legacy_preseed_manual_path=legacy_preseed_manual_path.name,
        net_image_http_path=net_image_http_path,
        os_name=Path(host.data.pxe.installer.image_source_url.path).stem,
        pxe=host.data.pxe,

        host=host, state=state,
    )

    #
    # Render the machine-specific preseed files
    #

    # Synology's SFTP permissions are unusual in that they don't allow
    # you to create directories (which we want to do in the files.template
    # operation after this one). As a workaround to that, we're going to
    # ensure the directory via the files.directory operation since it uses
    # just SSH.
    legacy_preseed_auto_dir_ssh_path = \
        host.data.pxe.http.root_dir / legacy_preseed_auto_dir.stem
    files.directory(
        name=f'Ensure {grub_dir} exists',
        path=legacy_preseed_auto_dir_ssh_path,
        present=True,

        host=host, state=state,
    )

    for machine in host.data.pxe.machines:
        machine_legacy_preseed_path = legacy_preseed_auto_dir / machine.hostname
        files.template(
            name=f'Render {machine_legacy_preseed_path}',
            src=deploy_dir / 'templates' / 'legacy-preseed-auto.seed.j2',
            dest=machine_legacy_preseed_path,
            create_remote_dir=False,

            machine=machine,
            pxe=host.data.pxe,

            host=host, state=state,
        )
