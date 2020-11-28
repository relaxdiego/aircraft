from importlib import import_module
from pathlib import Path
import os
import yaml

from aircraft.models.deployspec import inventory


class BlueprintNotFoundError(ValueError):

    def __init__(self, blueprint_shortname):
        msg = f"No blueprint named '{blueprint_shortname}'"
        super().__init__(msg)


class MainNotFoundError(AttributeError):

    def __init__(self, blueprint_shortname):
        msg = f"No main function for blueprint '{blueprint_shortname}'"
        super().__init__(msg)


# Opening the inventory file a second time (once in inventory.py and then
# another time here) isn't the most optimal solution so consider other
# options at anothe time. The best option would be for us to be able to
# obtain the inventory kind and api_version without re-opening the file.

deploy_spec = Path(os.environ['AIRCRAFT_DEPLOYSPEC'])
inventory_path = deploy_spec / 'inventory.yml'

with open(inventory_path, 'r') as inventory_fh:
    inventory = inventory.load(yaml.safe_load(inventory_fh))

blueprint_shortname = f"{inventory.kind}.{inventory.api_version}"
blueprint_fullname = f"aircraft.blueprints.{blueprint_shortname}.main"

try:
    blueprint = import_module(blueprint_fullname)
except ModuleNotFoundError as e:
    raise BlueprintNotFoundError(blueprint_shortname) from e

try:
    main_func = getattr(blueprint, 'main')
except AttributeError as e:
    raise MainNotFoundError(blueprint_shortname) from e

main_func()
