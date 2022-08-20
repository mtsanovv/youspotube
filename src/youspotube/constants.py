import sys
from tkinter import EXCEPTION

CONFIG_FILE_NAME = 'config.yml'

CONFIG_FILE_OPTION = '--use_cfg_file'
HELP_OPTION = '-h'

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

HELP_LINES = [
    "\nAvailable options:",
    "%-20sDisplays this help menu" % HELP_OPTION,
    "%-20sForces usage of config file instead of command line arguments" % CONFIG_FILE_OPTION,
    "\nIn case no options are to be specified, stick to the following usage:",
    "%s <origin> <youtube token> <spotify token> <playlist 1 youtube ID> <playlist 1 spotify ID> [<playlist n youtube ID> <playlist n spotify ID>]\n" % sys.argv[0],
    "where origin is the platform whose playlists should remain unchanged during the sync - either 'youtube' or 'spotify' (specify origin as 'both' in order to merge the playlists from both platforms\n"
    
]