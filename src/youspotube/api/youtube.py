from googleapiclient.discovery import build
from youspotube.exceptions import ConfigurationError


class YouTube:
    def __init__(self, api_key):
        try:
            self._init_connection(api_key)
            self._test_connection()
        except Exception as e:
            raise ConfigurationError("Test connection to YouTube API failed: %s" % str(e))

    def _init_connection(self, api_key):
        self.connection = build('youtube', 'v3', developerKey=api_key)

    def _test_connection(self):
        request = self.connection.channels().list(
            part="snippet,contentDetails,statistics",
            id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
        )
        request.execute()
