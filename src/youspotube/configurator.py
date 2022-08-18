from youspotube.argv import ArgvParser
from youspotube.param_collector import CfgFileParameterCollector, CmdLineParameterCollector

class Configuration:
    def __init__(self):
        self.is_help = 0
        self.origin = ''
        self.yt_token = ''
        self.spotify_token = ''
        self.youtube_playlists = []
        self.spotify_playlists = []
    def collect_parameters(self):
        argv_parser = ArgvParser()
        if argv_parser.is_help():
            self.is_help = 1
            return
        param_collector = CollectorFactory.create_collector(self, argv_parser.should_use_cfg_file())

class CollectorFactory:
    def create_collector(config, should_use_config_file):
        if should_use_config_file:
            return CfgFileParameterCollector(config)
        else:
            return CmdLineParameterCollector(config)