import os
import yaml

from devtools import debug


from aircraft.models.inventory import Inventory


# Currently a WIP. These are all mock ups and will end up becoming
# more complete down the line. For now, we are hardcoding the launch
# subcommand but this will eventually end up supporting multiple
# subcommands as we flesh out the CLI's details.

def main():
    launch()


def launch():
    load_inventory()


def load_inventory():
    inventory_path = os.path.join(os.getcwd(),
                                  'examples',
                                  'ha-kvm',
                                  'inventory.yml')

    with open(inventory_path, 'r') as inventory_fh:
        inventory_dict = yaml.safe_load(inventory_fh)

    inventory = Inventory(**inventory_dict)

    debug(inventory)
