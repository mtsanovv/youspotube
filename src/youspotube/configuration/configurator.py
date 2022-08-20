import youspotube.constants as constants
from youspotube.configuration.argv import ArgvParser
from youspotube.configuration.param_collector import CfgFileParameterCollector, CmdLineParameterCollector

class Configuration:
    def __init__(self):
        self.is_help = 0
        self.params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }


    def collect_parameters(self):
        argv_parser = ArgvParser()
        if argv_parser.is_help():
            self.is_help = 1
            return
        param_collector = CollectorFactory._create_collector(self.params, argv_parser.should_use_cfg_file())
        param_collector.collect()


    def is_help_requested(self):
        return self.is_help


    def get_params(self):
        return self.params


class CollectorFactory:
    def _create_collector(params, should_use_config_file):
        if should_use_config_file:
            return CfgFileParameterCollector(params)
        return CmdLineParameterCollector(params)