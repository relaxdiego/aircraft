import logging

from typing import (
    Callable,
    Dict,
)
from pydantic import (
    BaseModel,
)

from aircraft.executor import Executor

log = logging.getLogger("aircraft.Plan")


class UnsupportedApiVersionError(Exception):

    def __init__(self, version):
        super().__init__("Unsupported Plan API Version {}".format(version))


class Plan(BaseModel):
    name: str
    start_at: Callable
    rules: Dict[Callable, Dict[str, Callable]]

    def execute(self):
        log.debug("Executing plan '{}'".format(self.name))
        result = Executor(start_at=self.start_at, rules=self.rules)()
        log.debug("Plan '{}' completed".format(self.name))
        return result
