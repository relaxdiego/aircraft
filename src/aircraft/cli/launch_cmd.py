from pathlib import Path
import yaml

from aircraft.models.inventory import Inventory


class LaunchCmd:

    def __init__(self, manifest_dir):
        self.manifest_dir = manifest_dir

    def run(self):
        inventory_path = Path(self.manifest_dir) / 'inventory.yml'

        with open(inventory_path, 'r') as inventory_fh:
            inventory_dict = yaml.safe_load(inventory_fh)

        inventory = Inventory(**inventory_dict)

        import devtools; devtools.debug(inventory)  # NOQA: E702, E501
