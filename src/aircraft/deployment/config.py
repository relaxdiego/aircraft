from pyinfra.api import FactBase


class VirshNetworkNames(FactBase):
    requires_command = 'virsh'
    shell_executable = True
    command = "sudo virsh net-list --all --name || echo ''"

    def process(self, output=[]):
        return [name for name in output if len(name) > 0]


class VirshVirtualMachines(FactBase):
    requires_command = 'virsh'
    shell_executable = True
    command = "sudo virsh list --all --name || echo ''"

    def process(self, output=[]):
        return [name for name in output if len(name) > 0]
