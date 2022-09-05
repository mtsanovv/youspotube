import logging
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youspotube.exceptions import ConfigurationError
import youspotube.constants as constants
from youspotube.util.tools import Tools


class Spotify:
    def __init__(self, client_id, client_secret, tied_songs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tied_songs = tied_songs
        try:
            self._init_connection()
            self._test_connection()
        except Exception as e:
            raise ConfigurationError("Test connection to Spotify API failed: %s" % str(e))

    @property
    def connection(self):
        # _init_connection should have been called in order to be able to use this property
        auth_manager = self.spotify.auth_manager
        token_info = auth_manager.cache_handler.get_cached_token()
        if token_info is not None and auth_manager.is_token_expired(token_info):
            self._init_connection()
        return self.spotify

    def _init_connection(self):
        cache_path = Tools.get_filepath_relative_to_ysptb(constants.SPOTIFY_TOKEN_STORAGE_FILE)

        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=constants.SPOTIFY_SCOPE,
                redirect_uri=constants.SPOTIFY_CALLBACK_URL,
                client_id=self.client_id,
                client_secret=self.client_secret,
                cache_path=cache_path
            )
        )

    def _test_connection(self):
        self.connection.me()

    def _get_playlist_items(self, playlist_id):
        all_tracks = self.connection.playlist(playlist_id, 'tracks(items(track(name,id,duration_ms,artists(name))))')
        items = all_tracks['tracks']['items']

        return items

    def parse_playlist(self, playlist_details):
        playlist_id = playlist_details[constants.ORIGIN_SPOTIFY]
        playlist_items = self._get_playlist_items(playlist_id)

        playlist = {}

        for item in playlist_items:
            track = item['track']
            track_id = track['id']
            track_name = track['name']
            track_duration_ms = track['duration_ms']
            artists = []
            for artist in track['artists']:
                artists.append(artist['name'])
            playlist[track_id] = {
                'name': track_name,
                'artists': artists,
                'duration_ms': track_duration_ms
            }
        return playlist

    def youtube_playlist_to_track_ids(self, youtube_playlist):
        track_ids = []

        track_position = 0
        for video_id in youtube_playlist:
            video = youtube_playlist[video_id]

            track_id, track_title_artists, search_results = self._lookup_youtube_video_on_spotify(video, video_id)

            if track_id is None:
                continue

            track_ids.append({
                constants.SPOTIFY_TRACK_ID_DATA_KEY: track_id,
                constants.YOUTUBE_VIDEO_ID_DATA_KEY: video_id,
                constants.SPOTIFY_TRACK_TITLE_ARTISTS_DATA_KEY: track_title_artists,
                constants.YOUTUBE_VIDEO_TITLE_DATA_KEY: video['title'],
                constants.SEARCH_RESULTS_DATA_KEY: search_results,
                constants.TRACK_POSITION_DATA_KEY: track_position
            })

            track_position += 1

        return track_ids

    def _get_tied_track_id_to_video_id(self, video_id):
        for tie_name in self.tied_songs:
            tie = self.tied_songs[tie_name]
            if video_id == tie[constants.ORIGIN_YOUTUBE]:
                return tie[constants.ORIGIN_SPOTIFY]

        return None

    def _lookup_youtube_video_on_spotify(self, video, video_id):
        video_title = video['title']

        tied_track_id_to_video_id = self._get_tied_track_id_to_video_id(video_id)
        if tied_track_id_to_video_id is not None:
            logging.debug(
                "Using tied track ID '%s' to video '%s' instead of looking it up on Spotify" % (
                    tied_track_id_to_video_id,
                    video_title
                )
            )
            return tied_track_id_to_video_id, None, None

        logging.debug("Spotify search query: %s" % video_title)
        tracks_result = self.connection.search(video_title, constants.SPOTIFY_SEARCH_LIMIT, 0, 'track')['tracks']['items']

        if not tracks_result:
            logging.warning(
                "Could not find a relevant track in the top %s Spotify search results for: %s, song cannot be synchronized" % (
                    constants.SPOTIFY_SEARCH_LIMIT,
                    video_title
                )
            )
            return None, None, None

        track = tracks_result[0]
        track_id = track['id']
        track_name = track['name']
        track_artists = track['artists']
        track_artists_names = list(map(lambda x: x['name'], track_artists))
        track_title_artists = Tools.get_track_string(track_name, track_artists_names)

        return track_id, track_title_artists, tracks_result

    def _get_track_ids_from_spotify_playlist(self, playlist_items):
        track_ids = []

        for item in playlist_items:
            track = item['track']
            track_id = track['id']
            track_ids.append(track_id)

        return track_ids

    def get_missing_tracks_in_playlist(self, playlist_details, all_tracks):
        playlist_id = playlist_details[constants.ORIGIN_SPOTIFY]
        playlist_items = self._get_playlist_items(playlist_id)
        playlist_track_ids = self._get_track_ids_from_spotify_playlist(playlist_items)

        missing_tracks = []

        for track in all_tracks:
            track_search_results = track[constants.SEARCH_RESULTS_DATA_KEY]

            track_in_playlist = False

            if track_search_results is not None:
                for found_track in track_search_results:
                    found_track_id = found_track['id']

                    if found_track_id in playlist_track_ids:
                        track_in_playlist = True
                        break
            else:
                # a track without related YouTube search results is a tied track
                # we just look up those in the playlist directly
                track_in_playlist = track[constants.SPOTIFY_TRACK_ID_DATA_KEY] in playlist_track_ids

            if not track_in_playlist:
                missing_tracks.append(track)

        return missing_tracks

    def add_tracks_to_playlist(self, playlist_details, tracks_to_add):
        playlist_id = playlist_details[constants.ORIGIN_SPOTIFY]

        for track in tracks_to_add:
            playlist_length = len(self._get_playlist_items(playlist_id))
            track_id = track[constants.SPOTIFY_TRACK_ID_DATA_KEY]
            track_position = track[constants.TRACK_POSITION_DATA_KEY]

            if track_position > playlist_length - 1:
                track_position = None

            logging.debug("Pushing track '%s' to Spotify playlist '%s'" % (
                    track_id,
                    playlist_id
                )
            )

            self.connection.playlist_add_items(playlist_id, [track_id], track_position)

            time.sleep(constants.SLEEP_BETWEEN_PLAYLIST_PUSHES)
