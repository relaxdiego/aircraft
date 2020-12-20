from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)

blueprint_dir = Path(__file__).parent


class UnsupportedSchemaVersion(ValueError):

    def __init__(self, data_obj, supported_schema_versions):
        msg = f"{data_obj['model_name']} {data_obj['schema_version']} is not " \
              f"supported. Supported schema versions are {supported_schema_versions}"
        super().__init__(msg)


@deploy('Configure the DHCP server')
def configure(state=None, host=None):
    supported_schema_versions = [
        'v1beta1'
    ]

    if host.data.dhcp['schema_version'] in supported_schema_versions:
        filename = f"configure.sh.{host.data.dhcp['schema_version']}.j2"
    else:
        raise UnsupportedSchemaVersion(
            host.data.dhcp,
            supported_schema_versions
        )

    file_path = './configure.sh'

    files.template(
        name="Configure DHCP server",
        src=blueprint_dir / 'templates' / filename,
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


# @deploy('Configure the DHCP server')
# def unconfigure(state=None, host=None):
#     server.script_template(
#         name="Unconfigure DHCP server",
#         src=blueprint_dir / 'templates' / 'unconfigure.j2',
#         state=state, host=host,
#     )
