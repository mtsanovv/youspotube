class BaseYouspotubeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self, type):
        return "%s error: %s" % (type, self.value)
    def print_exception(self):
        print(str(self))

class ConfigurationError(BaseYouspotubeError):
    def __str__(self): 
        return super().__str__('Configuration')

class ExecutionError(BaseYouspotubeError):
    def __str__(self): 
        return super().__str__('Execution')