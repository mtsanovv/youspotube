import sys
import youspotube.constants as constants
from youspotube.exceptions import ConfigurationError

class ArgvParser:
    def __init__(self):
        argv_count = len(sys.argv)
        # argv always includes the executable or the script name as the first argument
        if argv_count < 2:
            raise ConfigurationError("Command line arguments should be more than one - run %s %s to see what they could be" % (sys.argv[0], constants.HELP_OPTION))
        if self.is_help() and argv_count > 2:
            raise ConfigurationError(self.get_no_more_arguments_error_message(constants.HELP_OPTION))
        if self.should_use_cfg_file() and argv_count > 2:
            raise ConfigurationError(self.get_no_more_arguments_error_message(constants.CONFIG_FILE_OPTION))
            
    
    def is_help(self):
        if constants.HELP_OPTION in sys.argv:
            return 1
        return 0
    
    def should_use_cfg_file(self):
        if constants.CONFIG_FILE_OPTION in sys.argv:
            return 1
        return 0
    
    def get_no_more_arguments_error_message(self, option):
        return "No other arguments should be passed to the program when the %s option is passed" % option