from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)

from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure the DHCP server')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1',
    ]

    validate_schema_version(host.data.dhcp, supported_schema_versions)

    filename = f"{host.data.dhcp.schema_version}/dhcp-configure.sh.j2"
    file_path = './dhcp-configure.sh'

    files.template(
        name='Render configuration script',
        src=deploy_dir / 'templates' / filename,
        dest=file_path,
        mode='700',
        state=state, host=host,
    )

    server.shell(
        name="Execute configuration script",
        commands=[
            file_path
        ],
        state=state, host=host,
    )


@deploy('Disable DHCP server')
def disable(state=None, host=None):
    supported_schema_versions = [
        'v1beta1'
    ]

    validate_schema_version(host.data.dhcp, supported_schema_versions)

    filename = f"{host.data.dhcp.schema_version}/dhcp-disable.sh.j2"
    file_path = './dhcp-disable.sh'

    files.template(
        name='Render configuration script',
        src=deploy_dir / 'templates' / filename,
        dest=file_path,
        mode='700',
        state=state, host=host,
    )

    server.shell(
        name="Execute configuration script",
        commands=[
            file_path
        ],
        state=state, host=host,
    )
