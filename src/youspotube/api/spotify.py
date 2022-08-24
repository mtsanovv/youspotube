import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youspotube.exceptions import ConfigurationError
import youspotube.constants as constants


class Spotify:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
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
        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=constants.SPOTIFY_SCOPE,
                redirect_uri=constants.SPOTIFY_CALLBACK_URL,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        )

    def _test_connection(self):
        self.connection.me()

    def parse_playlist(self, playlist_details):
        id = playlist_details[constants.ORIGIN_SPOTIFY]
        all_tracks = self.connection.playlist(id, 'tracks(items(track(name,id,duration_ms,artists(name))))')
        # output is something like this:
        # {'tracks': {'items': [{'track': {'artists': [{'name': 'Nedeljko Bajic Baja'}], 'id': '2S1o6wsyfgSK1uvGv91Knz', 'name': 'Zapisano je u vremenu'}}]}}
        tracks = all_tracks['tracks']['items']
        playlist = {}
        for item in tracks:
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
