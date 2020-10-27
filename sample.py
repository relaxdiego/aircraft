from random import randint
from time import sleep

from aircraft.plan import Plan


def waypoint(data):
    if data is None:
        data = [0]

    event = str(randint(1, 4))
    data = [data[0] + 1]
    sleep(1)

    return [event, data]


def endpoint(data):
    return ["done", data]


rules = {
    waypoint: {
        "1": waypoint,
        "2": waypoint,
        "3": waypoint,
        "4": endpoint,
    },
    endpoint: {}
}

Plan(api_version="v1beta1", start_at=waypoint, rules=rules).execute()
