import unittest
from unittest import mock
from unittest.mock import Mock

from youspotube.api.spotify import Spotify
from youspotube.exceptions import ConfigurationError
import youspotube.constants as constants


class SpotifyTest(unittest.TestCase):
    def setUp(self):
        self.spotify_mock = Mock()

    def test_Spotify_creation_no_error(self):
        expected_client_id = 1
        expected_client_secret = 2
        expected_tied_songs = {}

        Spotify.__init__(self.spotify_mock, expected_client_id, expected_client_secret, expected_tied_songs)

        self.assertEqual(expected_client_id, self.spotify_mock.client_id)
        self.assertEqual(expected_client_secret, self.spotify_mock.client_secret)
        self.assertIs(expected_tied_songs, self.spotify_mock.tied_songs)
        self.spotify_mock._init_connection.assert_called_once()
        self.spotify_mock._test_connection.assert_called_once()

    def test_Spotify_creation_error(self):
        expected_client_id = 1
        expected_client_secret = 2
        expected_tied_songs = {}
        error_reason = 'bad api'
        expected_error_message = "Configuration error: Test connection to Spotify API failed: %s" % error_reason
        self.spotify_mock._init_connection.side_effect = Exception(error_reason)

        with self.assertRaises(ConfigurationError) as expected_error:
            Spotify.__init__(self.spotify_mock, expected_client_id, expected_client_secret, expected_tied_songs)

        self.assertEqual(expected_client_id, self.spotify_mock.client_id)
        self.assertEqual(expected_client_secret, self.spotify_mock.client_secret)
        self.assertIs(expected_tied_songs, self.spotify_mock.tied_songs)
        self.assertEqual(str(expected_error.exception), expected_error_message)
        self.spotify_mock._init_connection.assert_called_once()
        self.spotify_mock._test_connection.assert_not_called()

    def test_Spotify_get_connection_without_init_connection(self):
        auth_manager = self.spotify_mock.spotify.auth_manager
        auth_manager.cache_handler.get_cached_token.return_value = None

        return_value = Spotify.connection.__get__(self.spotify_mock)

        auth_manager.is_token_expired.assert_not_called()
        self.spotify_mock._init_connection.assert_not_called()
        self.assertIs(return_value, self.spotify_mock.spotify)

    def test_Spotify_get_connection_with_init_connection(self):
        auth_manager = self.spotify_mock.spotify.auth_manager
        auth_manager.cache_handler.get_cached_token.return_value = 1
        auth_manager.is_token_expired.return_value = True

        return_value = Spotify.connection.__get__(self.spotify_mock)

        auth_manager.is_token_expired.assert_called_once_with(1)
        self.spotify_mock._init_connection.assert_called_once()
        self.assertIs(return_value, self.spotify_mock.spotify)

    @mock.patch('youspotube.api.spotify.SpotifyOAuth')
    @mock.patch('youspotube.api.spotify.spotipy')
    def test_Spotify_init_connection(self, spotipy_mock, oauth_mock):
        self.spotify_mock.client_id = 1
        self.spotify_mock.client_secret = 2

        Spotify._init_connection(self.spotify_mock)

        self.assertIs(self.spotify_mock.spotify, spotipy_mock.Spotify.return_value)
        spotipy_mock.Spotify.assert_called_once_with(auth_manager=oauth_mock.return_value)
        oauth_mock.assert_called_once_with(
            scope=constants.SPOTIFY_SCOPE,
            redirect_uri=constants.SPOTIFY_CALLBACK_URL,
            client_id=1,
            client_secret=2
        )

    def test_Spotify_test_connection(self):
        Spotify._test_connection(self.spotify_mock)

        self.spotify_mock.connection.me.assert_called_once()

    def test_Spotify_get_playlist_items(self):
        playlist_id = 1
        playlist_filter = 'tracks(items(track(name,id,duration_ms,artists(name))))'
        all_tracks = {
            'tracks': {
                'items': []
            }
        }
        self.spotify_mock.connection.playlist.return_value = all_tracks

        return_value = Spotify._get_playlist_items(self.spotify_mock, playlist_id)

        self.spotify_mock.connection.playlist.assert_called_once_with(playlist_id, playlist_filter)
        self.assertIs(return_value, all_tracks['tracks']['items'])

    def test_Spotify_parse_playlist(self):
        playlist_items = [{
            'track': {
                'artists': [{
                    'name': 'Nedeljko Bajic Baja'
                }],
                'id': '1',
                'name': 'Zapisano je u vremenu',
                'duration_ms': 300
            }
        }]
        parsed_playlist = {
            '1': {
                'name': 'Zapisano je u vremenu',
                'artists': ['Nedeljko Bajic Baja'],
                'duration_ms': 300
            }
        }
        playlist_details = {
            constants.ORIGIN_SPOTIFY: 3
        }
        self.spotify_mock._get_playlist_items.return_value = playlist_items

        return_value = Spotify.parse_playlist(self.spotify_mock, playlist_details)

        self.spotify_mock._get_playlist_items.assert_called_once_with(3)
        self.assertEqual(return_value, parsed_playlist)

    def test_Spotify_youtube_playlist_to_track_ids_bad_track(self):
        video_id = '1'
        youtube_playlist = {
            video_id: {}
        }
        self.spotify_mock._lookup_youtube_video_on_spotify.return_value = None, None, None

        return_value = Spotify.youtube_playlist_to_track_ids(self.spotify_mock, youtube_playlist)

        self.spotify_mock._lookup_youtube_video_on_spotify.assert_called_once_with(youtube_playlist[video_id], video_id)
        self.assertEqual(return_value, [])

    def test_Spotify_youtube_playlist_to_track_ids_ok_track(self):
        video_id = '1'
        video_title = 'title, yeah!'
        youtube_playlist = {
            video_id: {
                'title': video_title
            }
        }
        track_id = 1
        artists = 'test'
        search_result = {
            'result1': 'content1'
        }
        expected_track_ids_result = [{
            constants.SPOTIFY_TRACK_ID_DATA_KEY: track_id,
            constants.YOUTUBE_VIDEO_ID_DATA_KEY: video_id,
            constants.SPOTIFY_TRACK_TITLE_ARTISTS_DATA_KEY: artists,
            constants.YOUTUBE_VIDEO_TITLE_DATA_KEY: video_title,
            constants.SEARCH_RESULTS_DATA_KEY: search_result,
            constants.TRACK_POSITION_DATA_KEY: 0
        }]
        self.spotify_mock._lookup_youtube_video_on_spotify.return_value = track_id, artists, search_result

        return_value = Spotify.youtube_playlist_to_track_ids(self.spotify_mock, youtube_playlist)

        self.spotify_mock._lookup_youtube_video_on_spotify.assert_called_once_with(youtube_playlist[video_id], video_id)
        self.assertEqual(return_value, expected_track_ids_result)

    def test_Spotify_return_none_when_video_id_not_tied_to_track_id(self):
        self.spotify_mock.tied_songs = {}

        self.assertIs(Spotify._get_tied_track_id_to_video_id(self.spotify_mock, 1), None)

    def test_Spotify_return_track_id_tied_to_video_id(self):
        video_id = '1'
        track_id = '2'
        self.spotify_mock.tied_songs = {
            'song name': {
                constants.ORIGIN_YOUTUBE: video_id,
                constants.ORIGIN_SPOTIFY: track_id
            }
        }

        self.assertIs(Spotify._get_tied_track_id_to_video_id(self.spotify_mock, video_id), track_id)

    @mock.patch('youspotube.api.spotify.logging')
    def test_Spotify_lookup_youtube_video_on_spotify_tied_song(self, logging_mock):
        video_title = 'title, yeah'
        video_id = '1'
        tied_track_id = '2'
        video = {
            'title': video_title
        }
        expected_msg = "Using tied track ID '%s' to video '%s' instead of looking it up on Spotify" % (
            tied_track_id,
            video_title
        )
        self.spotify_mock._get_tied_track_id_to_video_id.return_value = tied_track_id

        return_value1, return_value2, return_value3 = Spotify._lookup_youtube_video_on_spotify(
            self.spotify_mock,
            video,
            video_id
        )

        self.spotify_mock._get_tied_track_id_to_video_id.assert_called_once_with(video_id)
        logging_mock.debug.assert_called_once_with(expected_msg)
        self.assertEqual([return_value1, return_value2, return_value3], [tied_track_id, None, None])

    @mock.patch('youspotube.api.spotify.logging')
    def test_Spotify_lookup_youtube_video_on_spotify_no_relevant_results(self, logging_mock):
        video_title = 'title, yeah'
        video_id = '1'
        video = {
            'title': video_title
        }
        tracks_result = {
            'tracks': {
                'items': []
            }
        }
        dbg = "Spotify search query: %s" % video_title
        wrn = "Could not find a relevant track in the top %s Spotify search results for: %s, song cannot be synchronized" % (
            constants.SPOTIFY_SEARCH_LIMIT,
            video_title
        )
        self.spotify_mock._get_tied_track_id_to_video_id.return_value = None
        self.spotify_mock.connection.search.return_value = tracks_result

        return_value1, return_value2, return_value3 = Spotify._lookup_youtube_video_on_spotify(
            self.spotify_mock,
            video,
            video_id
        )

        self.spotify_mock._get_tied_track_id_to_video_id.assert_called_once_with(video_id)
        logging_mock.debug.assert_called_once_with(dbg)
        self.spotify_mock.connection.search.assert_called_once_with(video_title, constants.SPOTIFY_SEARCH_LIMIT, 0, 'track')
        logging_mock.warning.assert_called_once_with(wrn)
        self.assertEqual([return_value1, return_value2, return_value3], [None, None, None])

    @mock.patch('youspotube.api.spotify.Tools')
    @mock.patch('youspotube.api.spotify.logging')
    def test_Spotify_lookup_youtube_video_on_spotify_relevant_result(self, logging_mock, tools_mock):
        video_title = 'title, yeah'
        video_id = '1'
        track_id = '2'
        track_title_artists = 'Test'
        video = {
            'title': video_title
        }
        tracks_result = {
            'tracks': {
                'items': [{
                    'id': track_id,
                    'name': 'aa',
                    'artists': [
                        {
                            'name': 'bb'
                        },
                        {
                            'name': 'cc'
                        }
                    ]
                }]
            }
        }
        dbg_msg = "Spotify search query: %s" % video_title
        self.spotify_mock._get_tied_track_id_to_video_id.return_value = None
        self.spotify_mock.connection.search.return_value = tracks_result
        tools_mock.get_track_string.return_value = track_title_artists

        return_value1, return_value2, return_value3 = Spotify._lookup_youtube_video_on_spotify(
            self.spotify_mock,
            video,
            video_id
        )

        self.spotify_mock._get_tied_track_id_to_video_id.assert_called_once_with(video_id)
        logging_mock.debug.assert_called_once_with(dbg_msg)
        self.spotify_mock.connection.search.assert_called_once_with(video_title, constants.SPOTIFY_SEARCH_LIMIT, 0, 'track')
        tools_mock.get_track_string.assert_called_once_with('aa', ['bb', 'cc'])
        self.assertEqual(
            [return_value1, return_value2, return_value3],
            [track_id, track_title_artists, tracks_result['tracks']['items']]
        )

    def test_Spotify_get_track_ids_from_spotify_playlist(self):
        playlist_items = [{
            'track': {
                'id': '1'
            }
        }]

        return_value = Spotify._get_track_ids_from_spotify_playlist(self.spotify_mock, playlist_items)

        self.assertEqual(return_value, ['1'])

    def test_Spotify_get_missing_tracks_in_playlist_tied_track(self):
        playlist_id = '2'
        track_id = '1'
        playlist_items = ['itema']
        playlist_track_ids = []
        playlist_details = {
            constants.ORIGIN_SPOTIFY: playlist_id
        }
        all_tracks = [{
            constants.SEARCH_RESULTS_DATA_KEY: None,
            constants.SPOTIFY_TRACK_ID_DATA_KEY: track_id
        }]
        self.spotify_mock._get_playlist_items.return_value = playlist_items
        self.spotify_mock._get_track_ids_from_spotify_playlist.return_value = playlist_track_ids

        return_value = Spotify.get_missing_tracks_in_playlist(self.spotify_mock, playlist_details, all_tracks)

        self.spotify_mock._get_playlist_items.assert_called_once_with(playlist_id)
        self.spotify_mock._get_track_ids_from_spotify_playlist.assert_called_once_with(playlist_items)
        self.assertEqual(return_value, [all_tracks[0]])

    def test_Spotify_get_missing_tracks_in_playlist_no_tied_track_no_search_results(self):
        playlist_id = '2'
        track_id = '1'
        playlist_items = ['itema']
        playlist_track_ids = [track_id]
        playlist_details = {
            constants.ORIGIN_SPOTIFY: playlist_id
        }
        all_tracks = [{
            constants.SEARCH_RESULTS_DATA_KEY: None,
            constants.SPOTIFY_TRACK_ID_DATA_KEY: track_id
        }]
        self.spotify_mock._get_playlist_items.return_value = playlist_items
        self.spotify_mock._get_track_ids_from_spotify_playlist.return_value = playlist_track_ids

        return_value = Spotify.get_missing_tracks_in_playlist(self.spotify_mock, playlist_details, all_tracks)

        self.spotify_mock._get_playlist_items.assert_called_once_with(playlist_id)
        self.spotify_mock._get_track_ids_from_spotify_playlist.assert_called_once_with(playlist_items)
        self.assertEqual(return_value, [])

    def test_Spotify_get_missing_tracks_in_playlist_search_result_not_in_playlist(self):
        playlist_id = '2'
        track_id = '1'
        playlist_items = ['itema']
        playlist_track_ids = []
        playlist_details = {
            constants.ORIGIN_SPOTIFY: playlist_id
        }
        all_tracks = [{
            constants.SEARCH_RESULTS_DATA_KEY: [{
                'id': track_id
            }],
            constants.SPOTIFY_TRACK_ID_DATA_KEY: track_id
        }]
        self.spotify_mock._get_playlist_items.return_value = playlist_items
        self.spotify_mock._get_track_ids_from_spotify_playlist.return_value = playlist_track_ids

        return_value = Spotify.get_missing_tracks_in_playlist(self.spotify_mock, playlist_details, all_tracks)

        self.spotify_mock._get_playlist_items.assert_called_once_with(playlist_id)
        self.spotify_mock._get_track_ids_from_spotify_playlist.assert_called_once_with(playlist_items)
        self.assertEqual(return_value, [all_tracks[0]])

    def test_Spotify_get_missing_tracks_in_playlist_search_result_in_playlist(self):
        playlist_id = '2'
        track_id = '1'
        playlist_items = ['itema']
        playlist_track_ids = [track_id]
        playlist_details = {
            constants.ORIGIN_SPOTIFY: playlist_id
        }
        all_tracks = [{
            constants.SEARCH_RESULTS_DATA_KEY: [{
                'id': track_id
            }],
            constants.SPOTIFY_TRACK_ID_DATA_KEY: track_id
        }]
        self.spotify_mock._get_playlist_items.return_value = playlist_items
        self.spotify_mock._get_track_ids_from_spotify_playlist.return_value = playlist_track_ids

        return_value = Spotify.get_missing_tracks_in_playlist(self.spotify_mock, playlist_details, all_tracks)

        self.spotify_mock._get_playlist_items.assert_called_once_with(playlist_id)
        self.spotify_mock._get_track_ids_from_spotify_playlist.assert_called_once_with(playlist_items)
        self.assertEqual(return_value, [])

    @mock.patch('youspotube.api.spotify.logging')
    @mock.patch('youspotube.api.spotify.time')
    def test_Spotify_append_track_to_playlist(self, time_mock, logging_mock):
        playlist_id = '2'
        track_id = '1'
        playlist_details = {
            constants.ORIGIN_SPOTIFY: playlist_id
        }
        tracks_to_add = [{
            constants.SPOTIFY_TRACK_ID_DATA_KEY: track_id,
            constants.TRACK_POSITION_DATA_KEY: 0
        }]
        expected_message = "Pushing track '%s' to Spotify playlist '%s'" % ( 
            track_id, 
            playlist_id 
        )
        self.spotify_mock._get_playlist_items.return_value = []

        Spotify.add_tracks_to_playlist(self.spotify_mock, playlist_details, tracks_to_add)

        self.spotify_mock._get_playlist_items.assert_called_once_with(playlist_id)
        logging_mock.debug.assert_called_once_with(expected_message)
        self.spotify_mock.connection.playlist_add_items.assert_called_once_with(playlist_id, [track_id], None)
        time_mock.sleep.assert_called_once_with(constants.SLEEP_BETWEEN_PLAYLIST_PUSHES)

    @mock.patch('youspotube.api.spotify.logging')
    @mock.patch('youspotube.api.spotify.time')
    def test_Spotify_add_track_to_specific_position_in_playlist(self, time_mock, logging_mock):
        playlist_id = '2'
        track_id = '1'
        playlist_details = {
            constants.ORIGIN_SPOTIFY: playlist_id
        }
        tracks_to_add = [{
            constants.SPOTIFY_TRACK_ID_DATA_KEY: track_id,
            constants.TRACK_POSITION_DATA_KEY: 0
        }]
        expected_message = "Pushing track '%s' to Spotify playlist '%s'" % ( 
            track_id, 
            playlist_id 
        )
        self.spotify_mock._get_playlist_items.return_value = ['dummy']

        Spotify.add_tracks_to_playlist(self.spotify_mock, playlist_details, tracks_to_add)

        self.spotify_mock._get_playlist_items.assert_called_once_with(playlist_id)
        logging_mock.debug.assert_called_once_with(expected_message)
        self.spotify_mock.connection.playlist_add_items.assert_called_once_with(playlist_id, [track_id], 0)
        time_mock.sleep.assert_called_once_with(constants.SLEEP_BETWEEN_PLAYLIST_PUSHES)
