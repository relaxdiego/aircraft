import logging

from typing import (
    Callable,
    Dict,
)
from pydantic import (
    BaseModel,
    validator
)

from aircraft.executor import Executor

log = logging.getLogger("aircraft.Plan")


class UnsupportedApiVersionError(Exception):

    def __init__(self, version):
        super().__init__("Unsupported Plan API Version {}".format(version))


class Plan(BaseModel):
    name: str
    api_version: str
    start_at: Callable
    rules: Dict[Callable, Dict[str, Callable]]

    @validator('api_version')
    def is_supported(cls, value):
        supported_versions = [
            "v1beta1"
        ]
        msg = "must be a supported version. Valid values are {}"
        assert value in ["v1beta1"], msg.format(supported_versions)
        return value

    def execute(self):
        log.debug("Executing plan '{}'".format(self.name))
        result = Executor(start_at=self.start_at, rules=self.rules)()
        log.debug("Plan '{}' completed".format(self.name))
        return result
