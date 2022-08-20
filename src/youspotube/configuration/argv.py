import sys
import youspotube.constants as constants
from youspotube.exceptions import ConfigurationError

class ArgvParser:
    def __init__(self):
        self.argv_count = len(sys.argv)
        self.check_argv()

    def check_argv(self):
        is_help = self.is_help()
        should_use_cfg_file = self.should_use_cfg_file()
        # argv always includes the executable or the script name as the first argument, no matter if it is a compiled python executable or not
        if is_help and self.argv_count > 2:
            raise ConfigurationError(self._get_no_more_arguments_error_message(constants.HELP_OPTION))
        if should_use_cfg_file and self.argv_count > 2:
            raise ConfigurationError(self._get_no_more_arguments_error_message(constants.CONFIG_FILE_OPTION))
        
        if not is_help and not should_use_cfg_file and self.argv_count < 6:
            raise ConfigurationError("Command line arguments should be at least six when %s and %s are not specified - run %s %s to see the correct usage" % (constants.HELP_OPTION, constants.CONFIG_FILE_OPTION, sys.argv[0], constants.HELP_OPTION))


    def is_help(self):
        if constants.HELP_OPTION in sys.argv:
            return True
        return False


    def should_use_cfg_file(self):
        if constants.CONFIG_FILE_OPTION in sys.argv:
            return True
        return False


    def _get_no_more_arguments_error_message(self, option):
        return "No other arguments should be passed to the program when the %s option is passed" % option


    def collect_cmd_line_params(self, params):
        params[constants.ORIGIN_PARAMETER] = sys.argv[1]
        params[constants.YT_TOKEN_PARAMETER] = sys.argv[2]
        params[constants.SPOTIFY_TOKEN_PARAMETER] = sys.argv[3]
        
        # first 4 arguments are always there and after that we put the youtube-spotify pairs so we should always have an even number of argv
        if self.argv_count % 2 != 0:
            raise ConfigurationError('Command line arguments should be an even number - are you missing a Spotify or a YouTube playlist ID?')
        
        for i in range(4, self.argv_count):
            if i % 2 == 0:
                params[constants.YT_PLAYLISTS_PARAMETER].append(sys.argv[i])
                continue
            params[constants.SPOTIFY_PLAYLISTS_PARAMETER].append(sys.argv[i])