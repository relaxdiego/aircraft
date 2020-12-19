from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import server

blueprint_dir = Path(__file__).parent


@deploy('Configure the DHCP server')
def configure(state=None, host=None):
    server.script_template(
        name="Configure DHCP server",
        src=blueprint_dir / 'templates' / 'configure.j2',
        state=state, host=host,
    )


@deploy('Configure the DHCP server')
def unconfigure(state=None, host=None):
    server.script_template(
        name="Unconfigure DHCP server",
        src=blueprint_dir / 'templates' / 'unconfigure.j2',
        state=state, host=host,
    )
