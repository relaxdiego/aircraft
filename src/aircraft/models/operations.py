from typing import (
    List,
)
from pydantic import (
    BaseModel,
)


class OperationSpec(BaseModel):
    blueprint: str
    operation: str = "main"

    # TODO: Add a validator here to check if the blueprint is valid?


class OperationSetSpec(BaseModel):
    operations: List[OperationSpec]

    class Config:
        allow_mutation = False
