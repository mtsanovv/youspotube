import logging
import youspotube.constants as constants
from youspotube.exceptions import ExecutionError


class Execution:
    def __init__(self, config):
        self.config = config
        self.params = self.config.get_params()
        self.playlists = self.params[constants.PLAYLISTS_PARAMETER]
        self.tied_songs = self.params[constants.TIED_SONGS_PARAMETER]
        self.spotify = self.config.get_spotify_connection()
        self.youtube = self.config.get_youtube_connection()

    def execute(self):
        logging.info("Synchronizing playlists: %s" % self.get_sync_arrow())
        self.sync_playlists()

    def get_sync_arrow(self):
        origin = self.params[constants.ORIGIN_PARAMETER]
        arrow_sides = ["YouTube", "Spotify"]
        if origin == constants.ORIGIN_SPOTIFY:
            arrow_sides.reverse()

        arrow = '-' * 10 + '> '
        if origin == constants.ORIGIN_BOTH:
            return (' <' + arrow).join(arrow_sides)
        return (' ' + arrow).join(arrow_sides)

    def sync_playlists(self):
        origin = self.params[constants.ORIGIN_PARAMETER]
        sync_method = "%s%s" % (constants.SYNC_FROM_METHOD_PREFIX, origin)
        if not hasattr(self, sync_method):
            raise ExecutionError("Origin '%s', accepted by the configuration, is not recognized by the executor" % origin)

        for playlist_name in self.playlists:
            logging.info("Synchronizing playlist '%s' from the configuration file" % playlist_name)

            try:
                getattr(self, sync_method)(self.playlists[playlist_name])
                logging.info("Finished synchronizing playlist '%s' from the configuration file" % playlist_name)
            except Exception as e:
                logging.warning(
                    "An error has occurred while synchronizing the '%s' playlist: %s" % (
                        playlist_name,
                        str(e)
                    )
                )

    def sync_from_spotify(self, playlist_details):
        spotify_playlist = self.spotify.parse_playlist(playlist_details)
        video_ids = self.youtube.spotify_playlist_to_video_ids(spotify_playlist)

        logging.info("Found %s/%s Spotify tracks on YouTube" % (len(video_ids), len(spotify_playlist)))

        needed_video_ids = self.youtube.get_missing_videos_in_playlist(playlist_details, video_ids)

        videos_to_push_count = len(needed_video_ids)
        if not videos_to_push_count:
            logging.info("Nothing to push to YouTube playlist")
            return

        logging.info("Pushing %s videos to YouTube playlist that are not in it" % videos_to_push_count)

        self.youtube.add_videos_to_playlist(playlist_details, needed_video_ids)

    def sync_from_youtube(self, playlist_details):
        pass

    def sync_from_both(self, playlist_details):
        self.sync_from_spotify()
        self.sync_from_youtube()
