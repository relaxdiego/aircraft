import logging

log = logging.getLogger("aircraft.Executor")


class Executor:

    def __init__(self, start_at, rules):
        self.__start_at = start_at
        self.__rules = rules

    def __call__(self):
        wp = self.__start_at

        while wp is not None:
            log.debug("Approaching Waypoint: {}".format(wp.__name__))
            event = wp()

            if event is None:
                raise WaypointDidNotReturnTuple(wp)

            log.debug("Event: {}".format(event))

            next_rules = self.__rules.get(wp)
            if next_rules == {}:
                break

            next_wp = next_rules.get(event, None)

            if next_wp is None:
                raise CannotTransitionError(wp, event)
                break

            wp = next_wp


class CannotTransitionError(Exception):

    def __init__(self, wp, event):
        msg = "Cannot find next waypoint from waypoint '{}' when event '{}' occurs"
        super().__init__(msg.format(wp.__name__, event))


class WaypointDidNotReturnTuple(Exception):

    def __init__(self, wp):
        msg = "Waypoint '{}' was excepted to return str, data but returned None"
        super().__init__(msg.format(wp.__name__))
