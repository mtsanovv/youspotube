from youspotube.configuration.argv import ArgvParser
from youspotube.util.yaml_parser import YamlParser
from youspotube.exceptions import ConfigurationError
import youspotube.constants as constants

class BaseParameterCollector:
    def __init__(self, params):
        self.params = params


class CfgFileParameterCollector(BaseParameterCollector):
    def collect(self):
        parsed_cfg_file = YamlParser.parse_config()
        self._validate_keys(parsed_cfg_file)
        self._copy_cfg_values(parsed_cfg_file)


    def _validate_keys(self, cfg):
        for param in self.params:
            if not param in cfg:
                raise ConfigurationError("Required parameter '%s' is missing in the configuration file" % param)

            config_param_type = type(self.params[param])
            cfg_file_param_type = type(cfg[param])

            if not config_param_type is cfg_file_param_type:
                raise ConfigurationError("Parameter '%s' is of type '%s' instead of '%s' in the configuration file" % (param, cfg_file_param_type, config_param_type))

        yt_playlists_length = len(cfg[constants.YT_PLAYLISTS_PARAMETER])
        spotify_playlists_length = len(cfg[constants.SPOTIFY_PLAYLISTS_PARAMETER])

        if yt_playlists_length == 0:
            raise ConfigurationError("No YouTube playlists defined in the configuration file")

        if spotify_playlists_length == 0:
            raise ConfigurationError("No Spotify playlists defined in the configuration file")

        if yt_playlists_length != spotify_playlists_length:
            raise ConfigurationError("Each YouTube playlist needs a matching Spotify one and there is a length mismatch between the list of YouTube playlists and the list of Spotify playlists in the configuration file")


    def _copy_cfg_values(self, cfg):
        for param in self.params:
            self.params[param] = cfg[param]


class CmdLineParameterCollector(BaseParameterCollector):
    def collect(self):
        argv_parser = ArgvParser()
        argv_parser.collect_cmd_line_params(self.params)