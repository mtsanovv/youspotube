from youspotube.api.spotify import Spotify
from youspotube.api.youtube import YouTube
from youspotube.configuration.param_validator import ParameterValidator
import youspotube.constants as constants
from youspotube.configuration.param_collector import CfgFileParameterCollector


class Configuration:
    def __init__(self):
        self.params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_CLIENT_ID_PARAMETER: '',
            constants.SPOTIFY_CLIENT_SECRET_PARAMETER: '',
            constants.PLAYLISTS_PARAMETER: {},
            constants.TIED_SONGS_PARAMETER: {}
        }

    def collect_parameters(self):
        param_collector = CfgFileParameterCollector(self.params)
        param_collector.collect()

    def validate_parameters(self):
        param_validator = ParameterValidator(self.params)
        param_validator.check_params()

    def connect_apis(self):
        self.spotify_connection = Spotify(
            self.params[constants.SPOTIFY_CLIENT_ID_PARAMETER],
            self.params[constants.SPOTIFY_CLIENT_SECRET_PARAMETER]
        )
        self.youtube_connection = YouTube(self.params[constants.YT_TOKEN_PARAMETER])

    def get_params(self):
        return self.params

    def get_spotify_conenction(self):
        return self.spotify_connection

    def get_youtube_connection(self):
        return self.youtube_connection
