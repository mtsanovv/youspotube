CONFIG_FILE_NAME = 'config.yml'

ORIGIN_PARAMETER = 'origin'
YT_TOKEN_PARAMETER = 'yt_token'
SPOTIFY_CLIENT_ID_PARAMETER = 'spotify_client_id'
SPOTIFY_CLIENT_SECRET_PARAMETER = 'spotify_client_secret'
PLAYLISTS_PARAMETER = 'playlists'
TIED_SONGS_PARAMETER = 'tied_songs'

NO_DATA_EXCEPTION_PARAMETERS = [TIED_SONGS_PARAMETER]

SPOTIFY_API_URL = 'https://api.spotify.com/v1/'
SPOTIFY_CALLBACK_URL = 'http://localhost:4466'
SPOTIFY_SCOPE = 'user-read-private playlist-modify-public playlist-read-private playlist-modify-private'
SPOTIFY_CACHE_FILE = '.cache'

YOUTUBE_API_URL = 'https://www.googleapis.com/youtube/v3/'

CONFIGURATION_ERROR_TYPE = 'Configuration'
EXECUTION_ERROR_TYPE = 'Execution'

EXIT_CODE_CONFIGURATION_ERROR = 1
EXIT_CODE_EXECUTION_ERROR = 2
