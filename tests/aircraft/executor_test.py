from unittest.mock import (
    call,
    create_autospec
)
from aircraft.executor import Executor


def waypoint(data=None):
    pass


def test_successfully_executes_a_plan():

    mock_wp_a = create_autospec(waypoint, spec_set=True)
    mock_wp_a.return_value = ["event_b", "data1"]

    mock_wp_b = create_autospec(waypoint, spec_set=True)
    mock_wp_b.return_value = ["event_c", "data2"]

    mock_wp_c = create_autospec(waypoint, spec_set=True)
    mock_wp_c.return_value = ["end", "data3"]

    rules = {
        mock_wp_a: {
            "event_b": mock_wp_b,
        },
        mock_wp_b: {
            "event_c": mock_wp_c,
        },
        mock_wp_c: {
            "_success_": True
        }
    }

    Executor(start_at=mock_wp_a, rules=rules)()

    assert mock_wp_a.call_count == 1
    assert mock_wp_a.call_args == call(None)

    assert mock_wp_b.call_count == 1
    assert mock_wp_b.call_args == call("data1")

    assert mock_wp_c.call_count == 1
    assert mock_wp_c.call_args == call("data2")
