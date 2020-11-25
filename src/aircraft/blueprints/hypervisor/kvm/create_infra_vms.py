from pyinfra.api import deploy
from pyinfra.operations import (
    server,
)


@deploy('Ensure infra VMs', data_defaults={})
def main(state, host):

    existing_vms = host.fact.virsh_virtual_machines
    infra_vm_count = host.data.infra_vm_count or 1

    for i in range(1, infra_vm_count + 1):
        vm_name = f'infra-{i}'

        if vm_name not in existing_vms:
            server.shell(
                name=f"Create VM '{vm_name}'",
                commands=[
                    'virt-install '
                    f'--name={vm_name} '
                    '--vcpus=2 '
                    '--memory=6144 '  # MiB
                    '--disk size=64 '  # GiB
                    '--cdrom=ubuntu-18.04.5-live-server-amd64.iso '
                    '--os-variant=ubuntu18.04 '
                    '--graphics vnc,listen=0.0.0.0 '
                    '--noautoconsole',

                    f'virsh autostart {vm_name}'
                ],
                sudo=True,

                host=host,
                state=state
            )
