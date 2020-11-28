from aircraft.blueprints.hypervisor.kvm import v1beta1


def main():
    v1beta1.install_packages()
    v1beta1.configure_bridged_network()
    v1beta1.create_guests()
