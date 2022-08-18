import sys
import youspotube.constants as constants
from youspotube.configurator import Configuration
from youspotube.executor import Execution
from youspotube.exceptions import ConfigurationError, ExecutionError

class Bootstrap:
    def __init__(self):
        config = Configuration()
        try:
            config.collect_parameters()
        except ConfigurationError as e:
            e.print_exception()
            sys.exit(constants.EXIT_CODE_CONFIGURATION_ERROR)

        executor = Execution(config)
        try:
            executor.execute()
        except ExecutionError as e:
            e.print_exception()
            sys.exit(constants.EXIT_CODE_EXECUTION_ERROR)
        