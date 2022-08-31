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
        logging.info("Synchronizing playlists: %s" % self.get_sync_direction())
        self.sync_playlists()

    def get_sync_direction(self):
        origin = self.params[constants.ORIGIN_PARAMETER]
        arrow_sides = ["Spotify", "YouTube"]
        if origin == constants.ORIGIN_YOUTUBE:
            arrow_sides.reverse()

        arrow = '-' * 10 + '> '
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
        youtube_playlist = self.youtube.parse_playlist(playlist_details)
        track_ids = self.spotify.youtube_playlist_to_track_ids(youtube_playlist)
        relevant_track_ids = self.youtube.get_relevant_spotify_tracks(track_ids)

        logging.info("Found %s/%s YouTube songs on Spotify" % (len(relevant_track_ids), len(youtube_playlist)))

        needed_track_ids = self.spotify.get_missing_tracks_in_playlist(playlist_details, relevant_track_ids)

        tracks_to_push_count = len(needed_track_ids)
        if not tracks_to_push_count:
            logging.info("Nothing to push to Spotify playlist")
            return

        logging.info("Pushing %s tracks to Spotify playlist that are not in it" % tracks_to_push_count)

        self.spotify.add_tracks_to_playlist(playlist_details, needed_track_ids)
