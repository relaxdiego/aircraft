import logging

log = logging.getLogger("aircraft.Executor")


class Executor:

    def __init__(self, start_at, rules):
        self.__start_at = start_at
        self.__rules = rules

    def __call__(self):
        wp = self.__start_at
        data = None

        while wp is not None:
            log.debug("Approaching Waypoint: {}".format(wp.__name__))
            event, data = wp(data)
            log.debug("Event occured: {}".format(event))
            log.debug("Data received: {}".format(event))
            wp = self.__rules.get(wp, {}).get(event, None)
