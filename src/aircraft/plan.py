from aircraft.plan_api.v1beta1 import PlanApiV1Beta1


class UnsupportedApiVersionError(Exception):

    def __init__(self, version):
        super().__init__("Unsupported Plan API Version {}".format(version))


class Plan:

    def __init__(self, api_version, start_at, rules):
        self.__driver = PlanApiV1Beta1(start_at=start_at,
                                       rules=rules)

    def execute(self):
        self.__driver.execute()

    def get_driver(self):
        return self.__driver
