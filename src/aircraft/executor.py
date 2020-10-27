class Executor:

    def __init__(self, start_at, rules):
        self.__start_at = start_at
        self.__rules = rules

    def __call__(self):
        wp = self.__start_at
        data = None

        while wp is not None:
            event, data = wp(data)
            wp = self.__rules.get(wp, {}).get(event, None)
