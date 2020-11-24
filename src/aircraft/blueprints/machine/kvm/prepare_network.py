from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)


@deploy('machine.kvm.prepare_network', data_defaults={})
def main(state, host):

    files.template(
        name='Render netplan config',
        src=str(Path(__file__).parent / 'templates' / 'netplan.yml.j2'),
        dest=host.fact.find_files('/etc/netplan/*.y*ml')[0],
        sudo=True,

        state=state,
        host=host,
    )

    server.shell(
        name='Run netplan generate',
        commands=['netplan generate'],
        sudo=True,

        state=state,
        host=host,
    )

    server.shell(
        name='Run netplan apply',
        commands=['netplan apply'],
        sudo=True,

        state=state,
        host=host,
    )
