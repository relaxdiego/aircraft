from aircraft import Plan
from aircraft.plan_api.v1beta1 import PlanApiV1Beta1


def test_init():
    def waypoint_a():
        pass

    def waypoint_b():
        pass

    def waypoint_c():
        pass

    api_version = "plan/v1beta1"
    rules = {
        waypoint_a: {
            "event_b": waypoint_b,
            "event_c": waypoint_c,
        },
        waypoint_b: {
            "event_c": waypoint_c,
        },
        waypoint_c: {
            "_success_": True
        }
    }

    plan = Plan(
        api_version=api_version,
        start_at=waypoint_a,
        rules=rules
    )

    assert type(plan.get_driver()) == PlanApiV1Beta1
