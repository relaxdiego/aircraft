import pytest
from pydantic import ValidationError

from aircraft.plan_api.v1beta1 import PlanApiV1Beta1


def sample_waypoint():
    pass


def test_it_fails_with_uncallable_start_at_field():

    with pytest.raises(ValidationError):
        PlanApiV1Beta1(
            start_at="bogus",
            rules={
                sample_waypoint: {
                    "event_a": sample_waypoint
                }
            }
        )


def test_it_fails_with_uncallable_rule_keys():

    with pytest.raises(ValidationError):
        PlanApiV1Beta1(
            start_at=object,
            rules={
                "uncallable": {
                    "event_a": object
                }
            }
        )
