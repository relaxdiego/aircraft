from importlib import import_module
from pathlib import Path
import os
import yaml

from aircraft.models.operations import OperationSetSpec

deploy_spec = Path(os.environ['AIRCRAFT_DEPLOY_SPEC'])

operations_path = deploy_spec / 'operations.yml'

with open(operations_path, 'r') as operations_fh:
    operation_set_spec = OperationSetSpec(**yaml.safe_load(operations_fh))

for operation_spec in operation_set_spec.operations:
    module_name = f"aircraft.blueprints.{operation_spec.blueprint}"
    module = import_module(module_name)
    getattr(module, operation_spec.operation)()
