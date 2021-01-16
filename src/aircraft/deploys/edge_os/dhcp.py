from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)

from aircraft.deploys.edge_os.models import v1beta3
from aircraft.validators import validate_schema_version

deploy_dir = Path(__file__).parent


@deploy('Configure EdgeOS DHCP')
def configure(state=None, host=None):
    supported_schema_versions = [
        v1beta3.DhcpData,
    ]

    validate_schema_version(host.data.dhcp, supported_schema_versions)

    filename = "dhcp-configure.sh.j2"
    file_path = './dhcp-configure.sh'

    files.template(
        name='Render configuration script',
        src=str(deploy_dir / 'templates' / filename),
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


@deploy('Delete EdgeOS DHCP Service')
def delete(state=None, host=None):
    supported_schema_versions = [
        v1beta3.DhcpData,
    ]

    validate_schema_version(host.data.dhcp, supported_schema_versions)

    filename = "dhcp-disable.sh.j2"
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
