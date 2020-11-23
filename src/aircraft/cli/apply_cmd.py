from pathlib import Path
import yaml

from pyinfra.api import Inventory

from aircraft.models.inventory import InventorySpec


class ApplyCmd:

    def __init__(self, manifest_dir):
        self.manifest_dir = manifest_dir

    def run(self):
        inventory_path = Path(self.manifest_dir) / 'inventory.yml'

        with open(inventory_path, 'r') as inventory_fh:
            inventory_dict = yaml.safe_load(inventory_fh)

        inventory_spec = InventorySpec(**inventory_dict)

        hosts = []
        for name, spec in inventory_spec.hosts.items():
            hosts.append((name, spec.data.dict()))

        groups_except_all = {name: spec for name, spec
                             in inventory_spec.groups.items()
                             if name != 'all'}
        groups = {}
        for name, spec in groups_except_all.items():
            groups[name] = (spec.hosts, spec.data.dict())

        global_data = inventory_spec.groups['all'].data.dict()

        inventory = Inventory((hosts, global_data), **groups)

        import devtools; devtools.debug(inventory)  # NOQA: E702, E501
