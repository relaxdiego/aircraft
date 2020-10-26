from unittest.mock import (
    call,
    patch,
)

from aircraft import Plan


@patch("aircraft.plan.PlanApiV1Beta1", autospec=True, spec_set=True)
def test_it_uses_PlanApiV1Beta1(mock_plan_api_v1beta1_cls):
    api_version = "plan/v1beta1"
    waypoint = object()
    rules = {}

    plan = Plan(
        api_version=api_version,
        start_at=waypoint,
        rules=rules
    )

    assert mock_plan_api_v1beta1_cls.call_count == 1
    assert mock_plan_api_v1beta1_cls.call_args == call(
        start_at=waypoint,
        rules=rules
    )

    assert plan.get_driver() == mock_plan_api_v1beta1_cls.return_value
