import youspotube.constants as constants

class BaseYouspotubeError(Exception):
    def __init__(self, message, exit_code):
        self.message = message
        self.exit_code = exit_code


    def __str__(self, type):
        return "%s error: %s" % (type, self.message)


    def print_exception(self):
        print(str(self))


    def get_exit_code(self):
        return self.exit_code


class ConfigurationError(BaseYouspotubeError):
    def __init__(self, message):
        super().__init__(message, constants.EXIT_CODE_CONFIGURATION_ERROR)


    def __str__(self): 
        return super().__str__(constants.CONFIGURATION_ERROR_TYPE)


class ExecutionError(BaseYouspotubeError):
    def __init__(self, message, exit_code = constants.EXIT_CODE_EXECUTION_ERROR):
        super().__init__(message, exit_code)


    def __str__(self): 
        return super().__str__(constants.EXECUTION_ERROR_TYPE)