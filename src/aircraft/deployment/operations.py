from importlib import import_module
from pathlib import Path
import os
import yaml

from pyinfra import host

from aircraft.models.operations import OperationSetSpec


class BlueprintNotFoundError(ValueError):

    def __init__(self, blueprint_shortname):
        msg = f"No blueprint named '{blueprint_shortname}'"
        super().__init__(msg)


class MainNotFoundError(AttributeError):

    def __init__(self, blueprint_shortname):
        msg = f"No main function for blueprint '{blueprint_shortname}'"
        super().__init__(msg)


deploy_spec = Path(os.environ['AIRCRAFT_DEPLOY_SPEC'])

operations_path = deploy_spec / 'operations.yml'

with open(operations_path, 'r') as operations_fh:
    operation_set_spec = OperationSetSpec(**yaml.safe_load(operations_fh))

for operation_spec in operation_set_spec.operations:
    if set(operation_spec.targets).intersection(host.groups + [str(host)]):
        for blueprint_shortname in operation_spec.blueprints:
            blueprint_fullname = f"aircraft.blueprints.{blueprint_shortname}"
            try:
                blueprint = import_module(blueprint_fullname)
            except ModuleNotFoundError as e:
                raise BlueprintNotFoundError(blueprint_shortname) from e

            try:
                main_func = getattr(blueprint, 'main')
            except AttributeError as e:
                raise MainNotFoundError(blueprint_shortname) from e

            main_func()
