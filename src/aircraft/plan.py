from typing import (
    Callable,
    Dict,
)
from pydantic import (
    BaseModel,
)

from aircraft.executor import Executor


class UnsupportedApiVersionError(Exception):

    def __init__(self, version):
        super().__init__("Unsupported Plan API Version {}".format(version))


class Plan(BaseModel):
    start_at: Callable
    rules: Dict[Callable, Dict[str, Callable]]

    def execute(self):
        Executor(start_at=self.start_at, rules=self.rules)()
