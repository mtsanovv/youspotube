import sys

CONFIG_FILE_NAME = 'config.yml'

ORIGIN_PARAMETER = 'origin'
YT_TOKEN_PARAMETER = 'yt_token'
SPOTIFY_TOKEN_PARAMETER = 'spotify_token'
YT_PLAYLISTS_PARAMETER = 'youtube_playlists'
SPOTIFY_PLAYLISTS_PARAMETER = 'spotify_playlists'

SPOTIFY_API_URL = 'https://api.spotify.com/v1/'
YOUTUBE_API_URL = 'https://www.googleapis.com/youtube/v3/'

CONFIGURATION_ERROR_TYPE = 'Configuration'
EXECUTION_ERROR_TYPE = 'Execution'

EXIT_CODE_CONFIGURATION_ERROR = 1
EXIT_CODE_EXECUTION_ERROR = 2