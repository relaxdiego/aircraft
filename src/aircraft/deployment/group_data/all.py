import os
from pathlib import Path
import yaml

from aircraft.models.inventory import InventorySpec

deploy_spec = Path(os.environ['AIRCRAFT_DEPLOYSPEC'])

inventory_path = deploy_spec / 'inventory.yml'

with open(inventory_path, 'r') as inventory_fh:
    inventory_spec = InventorySpec(**yaml.safe_load(inventory_fh))

for key, value in inventory_spec.groups['all'].data.dict().items():
    globals()[key] = value
