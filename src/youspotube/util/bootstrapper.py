from datetime import datetime
import getpass
import logging
import os
import sys
import atexit
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
        self.log_path = os.path.join(log_dir, log_filename)

        os.makedirs(constants.LOGS_DIR, exist_ok=True)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(constants.LOGGER_LOG_STOUD_FORMAT))
        stdout_handler.setLevel(logging.INFO)

        file_handler = logging.FileHandler(filename=self.log_path, mode='w')
        file_handler.setFormatter(logging.Formatter(constants.LOGGER_LOG_FILE_FORMAT))
        file_handler.setLevel(logging.DEBUG)

        logging.basicConfig(level=logging.NOTSET, handlers=[stdout_handler, file_handler])
        atexit.register(self.print_log_file_path)

        logging.debug("Running as effective user %s" % getpass.getuser())

    def print_log_file_path(self):
        print("Log file is available at '%s'" % self.log_path)
