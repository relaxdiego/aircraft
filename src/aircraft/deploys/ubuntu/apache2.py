from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
    files,
    server,
    systemd,
)

from aircraft.deploys.ubuntu.models import v1beta3
from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure apache2')
def configure(state=None, host=None):
    supported_schema_versions = [
        v1beta3.HttpData,
    ]

    validate_schema_version(host.data.http, supported_schema_versions)

    apt.packages(
        name='Install package',
        packages=['apache2'],
        sudo=True,

        state=state, host=host,
    )

    files.directory(
        name=f'Ensure HTTP root dir {host.data.http.root_dir}',
        path=str(host.data.http.root_dir),
        present=True,
        recursive=True,
        sudo=True,

        state=state, host=host,
    )

    apache_conf = files.template(
        name='Render config file',
        src=str(deploy_dir / 'templates' / 'apache2-directory.conf.j2'),
        dest=str(Path('/etc') / 'apache2' / 'conf-available' / 'root.conf'),
        mode='744',
        user='root',
        group='root',
        sudo=True,
        http=host.data.http,

        state=state, host=host,
    )

    server.shell(
        name='Enable root.conf',
        commands=[
            'a2enconf root'
        ],
        sudo=True,

        state=state, host=host,
    )

    systemd.service(
        name='Restart apache2',
        service='apache2',
        running=True,
        restarted=apache_conf.changed,
        sudo=True,

        state=state, host=host,
    )


@deploy('Uninstall apache2')
def uninstall(state=None, host=None):
    supported_schema_versions = [
        v1beta3.HttpData,
    ]

    validate_schema_version(host.data.http, supported_schema_versions)

    if 'apache2.service' in host.fact.systemd_status:
        systemd.service(
            name='Stop apache2',
            service='apache2',
            running=False,
            sudo=True,

            state=state, host=host,
        )

    files.file(
        name='Remove custom config',
        path=str(Path('/etc') / 'apache2' / 'conf-available' / 'root.conf'),
        present=False,
        sudo=True,

        state=state, host=host,
    )

    apt.packages(
        name='Ensure apache2 package is not present',
        packages=['apache2'],
        present=False,
        sudo=True,

        state=state, host=host,
    )
