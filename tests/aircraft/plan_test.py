from unittest.mock import (
    call,
    patch,
)
from uuid import uuid4

from aircraft import Plan


@patch("aircraft.plan.PlanApiV1Beta1", autospec=True, spec_set=True)
def test_it_initializes_a_plan_api_object(mock_plan_api_cls):
    api_version = "plan/v1beta1"
    waypoint = object()
    rules = {}

    plan = Plan(
        api_version=api_version,
        start_at=waypoint,
        rules=rules
    )

    assert mock_plan_api_cls.call_count == 1
    assert mock_plan_api_cls.call_args == call(
        start_at=waypoint,
        rules=rules
    )

    assert plan.get_driver() == mock_plan_api_cls.return_value


@patch("aircraft.plan.PlanApiV1Beta1", autospec=True, spec_set=True)
def test_it_executes_the_plan(mock_plan_api_cls):
    api_version = "bogus{}".format(uuid4())
    waypoint = object()
    rules = object()

    mock_plan_api_obj = mock_plan_api_cls.return_value

    Plan(api_version=api_version,
         start_at=waypoint,
         rules=rules).execute()

    assert mock_plan_api_obj.execute.call_count == 1
