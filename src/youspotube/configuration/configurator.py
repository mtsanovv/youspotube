import youspotube.constants as constants
from youspotube.configuration.param_collector import CfgFileParameterCollector

class Configuration:
    def __init__(self):
        self.params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }


    def collect_parameters(self):
        param_collector = CfgFileParameterCollector(self.params)
        param_collector.collect()


    def get_params(self):
        return self.params