from unittest.mock import (
    patch,
)
from uuid import uuid4

from aircraft.plan import (
    Plan,
)


def sample_waypoint():
    pass


@patch("aircraft.plan.Executor", autospec=True, spec_set=True)
def test_it_executes_the_plan(mock_executor_cls):
    api_version = "bogus{}".format(uuid4())
    rules = {
        sample_waypoint: {
            "event_a": sample_waypoint
        }
    }

    mock_executor_obj = mock_executor_cls

    Plan(api_version=api_version,
         start_at=sample_waypoint,
         rules=rules).execute()

    mock_executor_obj.call_count == 1
