# https://pydantic-docs.helpmanual.io/usage/models/
from pydantic import (
    BaseModel,
)


# The inventory must be able to validate its fields

class Inventory(BaseModel):
    hosts: dict
    groups: dict
