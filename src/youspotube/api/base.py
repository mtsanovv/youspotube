from youspotube.exceptions import ConfigurationError


class BaseAPI:
    def __init__(self, client_id, client_secret, tied_songs):
        classname = type(self).__name__

        self.client_id = client_id
        self.client_secret = client_secret
        self.tied_songs = tied_songs
        try:
            self._init_connection()
            self._test_connection()
        except Exception as e:
            raise ConfigurationError("Test connection to %s API failed: %s" % (classname, str(e)))