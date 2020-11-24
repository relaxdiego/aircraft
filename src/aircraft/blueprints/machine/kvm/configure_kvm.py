from pathlib import (
    Path,
)
from pyinfra.api import deploy
from pyinfra.operations import (
    apt,
    files,
    server,
)


@deploy('Configure KVM', data_defaults={})
def main(state, host):

    apt.packages(
        name='Install required packages',
        packages=[
            'qemu-kvm',
            'libvirt-daemon-system'
        ],
        sudo=True,
        update=True,
        cache_time=2592000,  # 30 days

        host=host,
        state=state,
    )

    networks = host.fact.command("sudo virsh net-list --all --name").split('\n')

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
            src=str(Path(__file__).parent / 'templates' / 'virsh-net.xml.j2'),
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
