import pytest
from pydantic import ValidationError
from unittest.mock import (
    call,
    patch,
)
from uuid import uuid4

from aircraft.plan import (
    Plan,
    PlanV1Beta1,
)


def sample_waypoint():
    pass


@patch("aircraft.plan.PlanV1Beta1", autospec=True, spec_set=True)
def test_it_initializes_a_plan_api_object(mock_plan_cls):
    api_version = "plan/v1beta1"
    waypoint = object()
    rules = {}

    Plan(
        api_version=api_version,
        start_at=waypoint,
        rules=rules
    )

    assert mock_plan_cls.call_count == 1
    assert mock_plan_cls.call_args == call(
        start_at=waypoint,
        rules=rules
    )


@patch("aircraft.plan.PlanV1Beta1", autospec=True, spec_set=True)
@patch("aircraft.executor.Executor", autospec=True, spec_set=True)
def test_it_executes_the_plan(mock_executor_cls, mock_plan_cls):
    api_version = "bogus{}".format(uuid4())
    waypoint = object()
    rules = object()

    mock_plan_obj = mock_plan_cls.return_value
    mock_executor_obj = mock_executor_cls

    Plan(api_version=api_version,
         start_at=waypoint,
         rules=rules).execute()

    mock_executor_obj.execute.call_count == 1
    mock_executor_cls.call_args == call(mock_plan_obj)


def test_it_fails_with_uncallable_start_at_field():

    with pytest.raises(ValidationError):
        PlanV1Beta1(
            start_at="bogus",
            rules={
                sample_waypoint: {
                    "event_a": sample_waypoint
                }
            }
        )


def test_it_fails_with_uncallable_rule_keys():

    with pytest.raises(ValidationError):
        PlanV1Beta1(
            start_at=object,
            rules={
                "uncallable": {
                    "event_a": object
                }
            }
        )
