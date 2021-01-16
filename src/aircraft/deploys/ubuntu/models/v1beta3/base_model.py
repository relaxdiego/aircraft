from pydantic import (
    BaseModel as PydanticBaseModel,
)


class BaseModel(PydanticBaseModel):
    class Config:
        # Quasi-immutable model
        allow_mutation = False
        # Prevent arbitrary fields from being provided upon initialization
        extra = 'forbid'
