import logging
import youspotube.constants as constants
from youspotube.exceptions import ExecutionError


class Execution:
    def __init__(self, config):
        self.config = config
        self.params = self.config.get_params()
        self.spotify = self.config.get_spotify_connection()
        self.youtube = self.config.get_youtube_connection()

    def execute(self):
        origin = self.params[constants.ORIGIN_PARAMETER]
        logging.info("Syncing playlists: %s" % self.get_sync_arrow())
        sync_method = "%s%s" % (constants.SYNC_FROM_METHOD_PREFIX, origin)
        if hasattr(self, sync_method):
            getattr(self, sync_method)()
            return
        raise ExecutionError("Origin '%s', accepted by the configuration, is not recognized by the executor" % origin)

    def get_sync_arrow(self):
        origin = self.params[constants.ORIGIN_PARAMETER]
        arrow_sides = ["YouTube", "Spotify"]
        if origin == constants.ORIGIN_SPOTIFY:
            arrow_sides.reverse()

        arrow = '-' * 10 + '> '
        if origin == constants.ORIGIN_BOTH:
            return (' <' + arrow).join(arrow_sides)
        return (' ' + arrow).join(arrow_sides)

    def sync_from_spotify(self):
        pass

    def sync_from_youtube(self):
        pass

    def sync_from_both(self):
        self.sync_from_spotify()
        self.sync_from_youtube()
