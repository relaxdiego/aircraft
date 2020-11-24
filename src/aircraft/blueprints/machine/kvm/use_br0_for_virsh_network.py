from pathlib import (
    Path,
)
from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)


@deploy('Use br0 for virsh-net', data_defaults={})
def main(state, host):
    networks = host.fact.virsh_network_names

    if 'default' in networks:
        server.shell(
            name="Remove virsh network 'default'",
            commands=[
                'virst net-undefine default',
                'virsh net-destroy default',
            ],

            host=host,
            state=state,
        )

    tmp_dir = f'{host.fact.home}/.aircraft/tmp'

    files.directory(
        name=f'Ensure {tmp_dir} exists',
        path=tmp_dir,
        present=True,

        host=host,
        state=state,
    )

    virsh_net_xml = f'{tmp_dir}/virsh-net.xml'

    if 'br0' not in networks:
        files.template(
            name='Render br0 network config',
            src=str(Path(__file__).parent / 'templates' / 'virsh-net-br0.xml.j2'),
            dest=virsh_net_xml,

            state=state,
            host=host,
        )

        server.shell(
            name="Define virsh network 'br0'",
            commands=[
                f"virsh net-define {virsh_net_xml}",
                "virsh net-start br0",
                "systemctl restart systemd-networkd",
            ],
            sudo=True,

            state=state,
            host=host,
        )
