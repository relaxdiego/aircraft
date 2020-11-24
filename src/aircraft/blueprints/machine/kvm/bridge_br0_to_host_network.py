from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)


@deploy('Bridge br0 to host network', data_defaults={})
def main(state, host):

    netplan_config = files.template(
        name='Render netplan config',
        src=str(Path(__file__).parent / 'templates' / 'netplan-bridged-br0.yml.j2'),
        dest=host.fact.find_files('/etc/netplan/*.y*ml')[0],
        sudo=True,

        state=state,
        host=host,
    )

    if netplan_config.changed:
        server.shell(
            name='Run netplan generate',
            commands=['netplan --debug generate'],
            sudo=True,

            state=state,
            host=host,
        )

        server.shell(
            name='Run netplan apply',
            commands=['netplan --debug apply'],
            sudo=True,

            state=state,
            host=host,
        )
