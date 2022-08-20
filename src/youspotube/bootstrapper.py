import sys
from youspotube.configurator import Configuration
from youspotube.executor import Execution
from youspotube.exceptions import ConfigurationError, ExecutionError
from youspotube.http import HttpUtil

class Bootstrap:
    def __init__(self):
        config = Configuration()
        try:
            HttpUtil.check_connectivity()
            config.collect_parameters()
        except ConfigurationError as e:
            e.print_exception()
            sys.exit(e.get_exit_code())

        executor = Execution(config)
        try:
            executor.execute()
        except ExecutionError as e:
            e.print_exception()
            sys.exit(e.get_exit_code())
        