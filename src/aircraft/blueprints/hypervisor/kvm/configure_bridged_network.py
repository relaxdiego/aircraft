from pathlib import Path

from pyinfra.api import deploy
from pyinfra.operations import (
    files,
    server,
)


@deploy('Configure bridged network', data_defaults={})
def main(state, host):

    netplan_config = files.template(
        name='Render netplan config',
        src=str(Path(__file__).parent / 'templates' / 'netplan_bridged.yml.j2'),
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

    if 'br0' not in networks:
        tmp_dir = f'{host.fact.home}/.aircraft/tmp'

        files.directory(
            name=f'Ensure {tmp_dir} exists',
            path=tmp_dir,
            present=True,

            host=host,
            state=state,
        )

        virsh_net_xml = f'{tmp_dir}/virsh-net.xml'

        files.template(
            name='Render virsh-net config',
            src=str(Path(__file__).parent / 'templates' / 'virsh_net_bridged.xml.j2'),
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
