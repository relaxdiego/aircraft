from aircraft import (
    Plan,
    ssh,
)

USERNAME = 'ubuntu'
HOSTNAME = 'kvm-1'
VM_NAME = "sample-001"


def main():
    rules = {
        check_if_vm_exists: {
            "present": exit,
            "absent": create_vm
        },
        create_vm: {
            "created": stop_vm,
        },
        stop_vm: {
            "stopped": ensure_pxe_first,
        },
        ensure_pxe_first: {
            "success": restart_vm
        },
        exit: {}
    }

    plan = Plan(name="Prepare Infra VMs",
                api_version="v1beta1",
                start_at=check_if_vm_exists,
                rules=rules)
    plan.execute()


def check_if_vm_exists():
    result = run_in_remote("virsh list | grep {}".format(VM_NAME))
    if result.returncode == 0:
        return "present"
    return "absent"


def create_vm():
    cmd_str = "sudo virt-install --name={} "\
              "--vcpus=1 " \
              "--memory=1024 " \
              "--disk size=40 " \
              "--cdrom=ubuntu-18.04.5-live-server-amd64.iso " \
              "--os-variant=ubuntu18.04 " \
              "--graphics vnc,listen=0.0.0.0 --noautoconsole " \
              .format(VM_NAME).replace(r'[ \s\n]+', ' ')

    result = run_in_remote(cmd_str)

    if result.returncode == 0:
        return "created"
    else:
        print(result.stderr)
        return "failed"


def exit():
    pass


def stop_vm():
    pass


def ensure_pxe_first():
    pass


def restart_vm():
    pass


def run_in_remote(command):
    return ssh(USERNAME, HOSTNAME, command)


if __name__ == "__main__":
    main()
