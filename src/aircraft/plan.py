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


class Plan:

    def __init__(self, api_version, start_at, rules):
        self.__plan = PlanV1Beta1(start_at=start_at,
                                  rules=rules)

    def execute(self):
        Executor(self.__plan).execute()


class PlanV1Beta1(BaseModel):
    start_at: Callable
    rules: Dict[Callable, Dict[str, Callable]]
