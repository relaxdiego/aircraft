from typing import Callable
from pydantic import BaseModel


class PlanApiV1Beta1(BaseModel):
    start_at: Callable
    rules: dict
