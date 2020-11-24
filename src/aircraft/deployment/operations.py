from importlib import import_module
from pathlib import Path
import os
import yaml

from pyinfra import host

from aircraft.models.operations import OperationSetSpec

deploy_spec = Path(os.environ['AIRCRAFT_DEPLOY_SPEC'])

operations_path = deploy_spec / 'operations.yml'

with open(operations_path, 'r') as operations_fh:
    operation_set_spec = OperationSetSpec(**yaml.safe_load(operations_fh))

for operation_spec in operation_set_spec.operations:
    if set(operation_spec.groups).intersection(host.groups):
        for blueprint_shortname in operation_spec.blueprints:
            blueprint_fullname = f"aircraft.blueprints.{blueprint_shortname}"
            blueprint = import_module(blueprint_fullname)
            getattr(blueprint, 'main')()
