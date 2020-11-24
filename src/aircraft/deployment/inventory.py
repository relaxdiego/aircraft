import os
from pathlib import Path
import yaml

from aircraft.models.inventory import InventorySpec

deploy_spec = Path(os.environ['AIRCRAFT_DEPLOY_SPEC'])

inventory_path = deploy_spec / 'inventory.yml'

with open(inventory_path, 'r') as inventory_fh:
    inventory_spec = InventorySpec(**yaml.safe_load(inventory_fh))

for group_name, group_spec in inventory_spec.groups.items():
    if group_name == 'all':
        continue

    globals()[group_name] = []
    for host in group_spec.hosts:
        merged_data = {
            **{k: v for k, v
               in group_spec.data.dict().items()
               if v is not None},
            **{k: v for k, v
               in inventory_spec.hosts[host].data.dict().items()
               if v is not None},
        }
        globals()[group_name].append((host, merged_data))
