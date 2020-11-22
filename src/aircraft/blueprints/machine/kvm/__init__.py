from os import path

from pyinfra import host
from pyinfra.api import deploy, DeployError
from pyinfra.operations import files


@deploy('Prepare Host', data_defaults={})
def prepare_host(state, host):

    files.template(
        name='Render netplan configuration',
        src=path.join(
            path.dirname(__file__), 'templates', 'netplan.yaml.j2'
        ),
        dest=host.fact.find_files('/etc/netplan/*.y*ml')[0],

        state=state,
        host=host,
    )
