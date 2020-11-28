from importlib import import_module

from pydantic import BaseModel


def load(d):
    inventory_spec = GenericInventorySpec(**d)
    module = import_module('aircraft.models.deployspec.inventory.'
                           f'{inventory_spec.kind}.{inventory_spec.api_version}')
    return module.Inventory(**d)


class GenericInventorySpec(BaseModel):
    kind: str
    api_version: str
    spec: dict
