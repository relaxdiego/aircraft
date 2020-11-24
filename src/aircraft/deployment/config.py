from pyinfra.api import FactBase


class VirshNetworkNames(FactBase):
    requires_command = 'virsh'
    shell_executable = True
    command = "sudo virsh net-list --all --name"

    def process(self, output):
        return [name for name in output if len(name) > 0]
