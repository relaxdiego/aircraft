from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import files


@deploy('Prepare KVM host network', data_defaults={})
def main(state, host):

    files.template(
        name='Render netplan configuration',
        src=str(Path(__file__).parent / 'templates' / 'netplan.yml.j2'),
        dest=str(Path('/tmp') / 'netplan.yml'),

        state=state,
        host=host,
    )
