from typing import (
    Callable,
    Dict,
)
from pydantic import (
    BaseModel,
)


class PlanApiV1Beta1(BaseModel):
    start_at: Callable
    rules: Dict[Callable, Dict[str, Callable]]

    def execute(self):
        pass
