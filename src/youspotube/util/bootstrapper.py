from datetime import datetime
import getpass
import logging
import os
import sys
from youspotube.configuration.configurator import Configuration
from youspotube.execution.executor import Execution
from youspotube.exceptions import ConfigurationError, ExecutionError
from youspotube.util.http import HttpUtil
import youspotube.constants as constants


class Bootstrap:
    def __init__(self):
        try:
            self.configure_logging()
            config = Configuration()
            HttpUtil.check_connectivity()
            config.collect_parameters()
            config.connect_apis()
            config.validate_parameters()
        except ConfigurationError as e:
            e.print_exception()
            sys.exit(e.get_exit_code())

        executor = Execution(config)
        try:
            executor.execute()
        except ExecutionError as e:
            e.print_exception()
            sys.exit(e.get_exit_code())

    def configure_logging(self):
        log_filename = constants.LOG_FILE % "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
        log_dir = os.path.join(os.getcwd(), constants.LOGS_DIR)
        log_path = os.path.join(log_dir, log_filename)

        os.makedirs(constants.LOGS_DIR, exist_ok=True)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)

        file_handler = logging.FileHandler(filename=log_path, mode='w')
        file_handler.setLevel(logging.DEBUG)

        logging.basicConfig(level=logging.NOTSET, format=constants.LOGGER_FORMAT, handlers=[stdout_handler, file_handler])

        logging.debug("Running as effective user %s" % getpass.getuser())
