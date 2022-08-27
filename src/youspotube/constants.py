CONFIG_FILE_NAME = 'config.yml'

LOGGER_LOG_FILE_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
LOGGER_LOG_STOUD_FORMAT = "%(message)s"
LOGS_DIR = 'logs'
LOG_FILE = "ysptb_%s.log"

CHECK_PARAM_METHOD_PREFIX = 'check_'
SYNC_FROM_METHOD_PREFIX = 'sync_from_'

ORIGIN_YOUTUBE = 'youtube'
ORIGIN_SPOTIFY = 'spotify'
ORIGIN_BOTH = 'both'
ORIGINS = [ORIGIN_YOUTUBE, ORIGIN_SPOTIFY, ORIGIN_BOTH]
REQUIRED_KEYS_PLAYLISTS_SONGS = [ORIGIN_YOUTUBE, ORIGIN_SPOTIFY]

ORIGIN_PARAMETER = 'origin'
YOUTUBE_CLIENT_ID_PARAMETER = 'youtube_client_id'
YOUTUBE_CLIENT_SECRET_PARAMETER = 'youtube_client_secret'
SPOTIFY_CLIENT_ID_PARAMETER = 'spotify_client_id'
SPOTIFY_CLIENT_SECRET_PARAMETER = 'spotify_client_secret'
PLAYLISTS_PARAMETER = 'playlists'
TIED_SONGS_PARAMETER = 'tied_songs'

NO_DATA_EXCEPTION_PARAMETERS = [TIED_SONGS_PARAMETER]

SPOTIFY_API_URL = 'https://api.spotify.com/v1/'
SPOTIFY_CALLBACK_URL = 'http://localhost:4466'
SPOTIFY_SCOPE = 'user-read-private playlist-modify-public playlist-read-private playlist-modify-private'

YOUTUBE_API_URL = 'https://www.googleapis.com/youtube/v3/'
YOUTUBE_TOKEN_STORAGE_FILE = '.youtube_cache'
YOUTUBE_SCOPE = 'https://www.googleapis.com/auth/youtube'
MAX_YOUTUBE_SPOTIFY_DURATION_DELTA_SECONDS = 15
YOUTUBE_SPOTIFY_DURATION_DELTA_DATA_KEY = 'spotify_youtube_length_difference'
YOUTUBE_VIDEO_ID_DATA_KEY = 'video_id'
SEARCH_RESULTS_KEY = 'search_results'
TRACK_POSITION_KEY = 'track_position'
INITIAL_SEARCH_LIMIT = 3
EXTENDED_SEARCH_LIMIT = 7
SLEEP_BETWEEN_YOUTUBE_PLAYLIST_PUSHES = 3

CONFIGURATION_ERROR_TYPE = 'Configuration'
EXECUTION_ERROR_TYPE = 'Execution'

EXIT_CODE_CONFIGURATION_ERROR = 1
EXIT_CODE_EXECUTION_ERROR = 2
