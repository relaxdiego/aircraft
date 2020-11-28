import os
from pathlib import Path
import yaml

from aircraft.models.deployspec import inventory

deploy_spec = Path(os.environ['AIRCRAFT_DEPLOYSPEC'])
inventory_path = deploy_spec / 'inventory.yml'

with open(inventory_path, 'r') as inventory_fh:
    inventory = inventory.load(yaml.safe_load(inventory_fh))

for group_spec in inventory.spec.groups:
    if group_spec.name == 'all':
        continue

    globals()[group_spec.name] = []
    for member_name in group_spec.members:
        # TODO: This responsibility should be moved to the Inventory model
        host = next((host for host in inventory.spec.hosts if host.name == member_name))
        merged_data = {
            **{k: v for k, v
               in group_spec.data.dict().items()
               if v is not None},
            **{k: v for k, v
               in host.data.dict().items()
               if v is not None},
        }
        globals()[group_spec.name].append((member_name, merged_data))
