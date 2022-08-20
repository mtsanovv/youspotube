import youspotube.constants as constants

class BaseYouspotubeError(Exception):
    def __init__(self, value, exit_code):
        self.value = value
        self.exit_code = exit_code


    def __str__(self, type):
        return "%s error: %s" % (type, self.value)


    def print_exception(self):
        print(str(self))


    def get_exit_code(self):
        return self.exit_code


class ConfigurationError(BaseYouspotubeError):
    def __init__(self, value):
        super().__init__(value, constants.EXIT_CODE_CONFIGURATION_ERROR)


    def __str__(self): 
        return super().__str__('Configuration')


class ExecutionError(BaseYouspotubeError):
    def __init__(self, value, exit_code = constants.EXIT_CODE_EXECUTION_ERROR):
        super().__init__(value, exit_code)


    def __str__(self): 
        return super().__str__('Execution')