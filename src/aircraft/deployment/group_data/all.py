import os
from pathlib import Path
import yaml

from aircraft.models.deployspec import inventory

deploy_spec = Path(os.environ['AIRCRAFT_DEPLOYSPEC'])
inventory_path = deploy_spec / 'inventory.yml'

with open(inventory_path, 'r') as inventory_fh:
    inventory = inventory.load(yaml.safe_load(inventory_fh))
