from importlib import import_module
from pathlib import Path
import os
import yaml

from aircraft.models.operations import OperationSetSpec

manifest_dir = Path(os.environ['AIRCRAFT_MANIFEST_DIR'])
operations_path = manifest_dir / 'operations.yml'

with open(operations_path, 'r') as operations_fh:
    operations_dict = yaml.safe_load(operations_fh)

operation_set_spec = OperationSetSpec(**operations_dict)

for operation_spec in operation_set_spec.operations:
    module_name = f"aircraft.blueprints.{operation_spec.blueprint}"
    module = import_module(module_name)
    module.main()
    getattr(module, operation_spec.operation)()
