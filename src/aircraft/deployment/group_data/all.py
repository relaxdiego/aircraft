import os
from pathlib import Path
import yaml

from aircraft.models.inventory import InventorySpec

deploy_spec = Path(os.environ['AIRCRAFT_DEPLOY_SPEC'])

inventory_path = deploy_spec / 'inventory.yml'

with open(inventory_path, 'r') as inventory_fh:
    inventory_dict = yaml.safe_load(inventory_fh)

inventory_spec = InventorySpec(**inventory_dict)

for key, value in inventory_spec.groups['all'].data.dict().items():
    globals()[key] = value
