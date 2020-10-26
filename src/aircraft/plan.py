from aircraft.plan_api.v1beta1 import PlanApiV1Beta1


class UnsupportedApiVersionError(Exception):

    def __init__(self, version):
        super().__init__("Unsupported Plan API Version {}".format(version))


class Plan:

    def __init__(self, api_version, start_at, rules):
        self.__api_version = api_version
        self.__start_at = start_at
        self.__rules = rules

    def get_driver(self):
        if self.__api_version == "plan/v1beta1":
            self.__driver = PlanApiV1Beta1()
        else:
            raise UnsupportedApiVersionError(self.__api_version)

        return self.__driver
