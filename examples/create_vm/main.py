from aircraft import Plan


def main():
    rules = {
        create_vm: {
            "created": stop_vm,
        },
        stop_vm: {
            "stopped": ensure_pxe_first,
        },
        ensure_pxe_first: {
            "success": restart_vm
        },
        restart_vm: {}
    }

    plan = Plan(name="Prepare Infra VMs",
                api_version="v1beta1",
                start_at=create_vm,
                rules=rules)
    plan.execute()


def create_vm():
    virt_install(
        name='vm',
        vcpus=2,
        memory="6GB",
        disks=[
            {
                "size": "64GB"
            }
        ],
        cdrom="ubuntu-18.04.5-live-server-amd64.iso",
        os_variant="ubuntu18.04",
        graphics="vnc,listen=0.0.0.0",
        autoconsole=False
    )
    return "created"


def stop_vm():
    pass


def ensure_pxe_first():
    pass


def restart_vm():
    pass


def virt_install():
    pass

if __name__ == "__main__":
    main()
