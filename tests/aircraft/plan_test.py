from aircraft import Plan


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

    assert plan.api_version == api_version
    assert plan.start_at == waypoint_a
    assert plan.rules == rules
