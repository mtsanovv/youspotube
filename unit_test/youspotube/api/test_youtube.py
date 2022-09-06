import unittest
from unittest import mock
from unittest.mock import Mock

import os
from youspotube.api.youtube import YouTube
import youspotube.constants as constants
from youspotube.util.tools import Tools


class YouTubeTest(unittest.TestCase):
    def setUp(self):
        self.youtube_mock = Mock()

    def test_YouTube_get_connection_without_init_connection(self):
        self.youtube_mock._get_credentials.return_value.expired = False

        return_value = YouTube.connection.__get__(self.youtube_mock)

        self.youtube_mock._init_connection.assert_not_called()
        self.assertIs(return_value, self.youtube_mock.youtube)

    def test_YouTube_get_connection_with_init_connection(self):
        credentials_mock = self.youtube_mock._get_credentials.return_value
        credentials_mock.expired = True

        return_value = YouTube.connection.__get__(self.youtube_mock)

        self.youtube_mock._init_connection.assert_called_once_with(credentials_mock)
        self.assertIs(return_value, self.youtube_mock.youtube)

    @mock.patch('youspotube.api.youtube.build')
    def test_YouTube_init_connection_no_credentials_argument(self, build_mock):
        credentials_mock = self.youtube_mock._get_credentials.return_value
        credentials_mock.expired = False

        YouTube._init_connection(self.youtube_mock)

        self.youtube_mock._get_credentials.assert_called_once()
        build_mock.assert_called_once_with(
            'youtube',
            'v3',
            credentials=credentials_mock,
            static_discovery=False,
            cache_discovery=False
        )
        self.assertIs(self.youtube_mock.youtube, build_mock.return_value)

    @mock.patch('youspotube.api.youtube.Request')
    @mock.patch('youspotube.api.youtube.build')
    def test_YouTube_init_connection_expired_credentials_as_argument(self, build_mock, request_mock):
        credentials_mock = Mock()
        credentials_mock.expired = True

        YouTube._init_connection(self.youtube_mock, credentials_mock)

        self.youtube_mock._get_credentials.assert_not_called()
        credentials_mock.refresh.assert_called_once_with(request_mock.return_value)
        self.youtube_mock._save_credentials.assert_called_once_with(credentials_mock)
        build_mock.assert_called_once_with(
            'youtube',
            'v3',
            credentials=credentials_mock,
            static_discovery=False,
            cache_discovery=False
        )
        self.assertIs(self.youtube_mock.youtube, build_mock.return_value)

    @mock.patch('builtins.open')
    @mock.patch('youspotube.api.youtube.InstalledAppFlow')
    @mock.patch('youspotube.api.youtube.os')
    @mock.patch('youspotube.api.youtube.Tools')
    def test_YouTube_get_credentials_nonexistent_credentials_file(self, tools_mock, os_mock, installedappflow_mock, open_mock):
        expected_client_id = 1
        expected_client_secret = 2
        self.youtube_mock.client_id = expected_client_id
        self.youtube_mock.client_secret = expected_client_secret
        credentials_file_path = os.path.join('.', 'credentials_file')
        flow_mock = installedappflow_mock.from_client_config.return_value
        credentials_mock = flow_mock.run_local_server.return_value
        expected_client_config = {
            "installed": {
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "client_id": expected_client_id,
                "client_secret": expected_client_secret
            }
        }
        expected_scopes = [constants.YOUTUBE_SCOPE]
        tools_mock.get_filepath_relative_to_ysptb.return_value = credentials_file_path
        os_mock.path.exists.return_value = False

        return_value = YouTube._get_credentials(self.youtube_mock)

        tools_mock.get_filepath_relative_to_ysptb.assert_called_once_with(constants.YOUTUBE_TOKEN_STORAGE_FILE)
        os_mock.path.exists.assert_called_once_with(credentials_file_path)
        installedappflow_mock.from_client_config.assert_called_once_with(
            client_config=expected_client_config,
            scopes=expected_scopes
        )
        flow_mock.run_local_server.assert_called_once_with(port=4467)
        self.youtube_mock._save_credentials.assert_called_once_with(credentials_mock)
        open_mock.assert_not_called()
        self.assertIs(return_value, credentials_mock)

    @mock.patch('youspotube.api.youtube.pickle')
    @mock.patch('builtins.open')
    @mock.patch('youspotube.api.youtube.InstalledAppFlow')
    @mock.patch('youspotube.api.youtube.os')
    @mock.patch('youspotube.api.youtube.Tools')
    def test_YouTube_get_credentials_existing_credentials_file(self, tools_mock, os_mock,
                                                               installedappflow_mock, open_mock, pickle_mock):
        expected_client_id = 1
        expected_client_secret = 2
        self.youtube_mock.client_id = expected_client_id
        self.youtube_mock.client_secret = expected_client_secret
        credentials_file_path = os.path.join('.', 'credentials_file')
        credentials_mock = pickle_mock.load.return_value
        tools_mock.get_filepath_relative_to_ysptb.return_value = credentials_file_path
        os_mock.path.exists.return_value = True

        return_value = YouTube._get_credentials(self.youtube_mock)

        tools_mock.get_filepath_relative_to_ysptb.assert_called_once_with(constants.YOUTUBE_TOKEN_STORAGE_FILE)
        os_mock.path.exists.assert_called_once_with(credentials_file_path)
        installedappflow_mock.from_client_config.assert_not_called()
        self.youtube_mock._save_credentials.assert_not_called()
        open_mock.assert_called_once_with(credentials_file_path, 'rb')
        pickle_mock.load.assert_called_once_with(open_mock.return_value.__enter__.return_value)
        self.assertIs(return_value, credentials_mock)

    @mock.patch('youspotube.api.youtube.pickle')
    @mock.patch('builtins.open')
    @mock.patch('youspotube.api.youtube.Tools')
    def test_YouTube_save_credentials(self, tools_mock, open_mock, pickle_mock):
        credentials_mock = Mock()
        credentials_file_path = os.path.join('.', 'credentials_file')
        tools_mock.get_filepath_relative_to_ysptb.return_value = credentials_file_path

        YouTube._save_credentials(self.youtube_mock, credentials_mock)

        tools_mock.get_filepath_relative_to_ysptb.assert_called_once_with(constants.YOUTUBE_TOKEN_STORAGE_FILE)
        open_mock.assert_called_once_with(credentials_file_path, 'wb')
        pickle_mock.dump.assert_called_once_with(credentials_mock, open_mock.return_value.__enter__.return_value)

    def test_YouTube_test_connection(self):
        channels_request_mock = self.youtube_mock.connection.channels.return_value
        list_request_mock = channels_request_mock.list.return_value

        YouTube._test_connection(self.youtube_mock)

        channels_request_mock.list.assert_called_once_with(
            part="snippet,contentDetails,statistics",
            id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
        )
        list_request_mock.execute.assert_called_once()

    def test_YouTube_spotify_playlist_to_video_ids_no_video_results(self):
        expected_track_id = '1'
        spotify_playlist = {
            expected_track_id: {}
        }
        self.youtube_mock._lookup_spotify_track_on_youtube.return_value = None, None

        return_value = YouTube.spotify_playlist_to_video_ids(self.youtube_mock, spotify_playlist)

        self.youtube_mock._lookup_spotify_track_on_youtube.assert_called_once_with(
            spotify_playlist[expected_track_id],
            expected_track_id
        )
        self.assertEqual(return_value, [])

    def test_YouTube_spotify_playlist_to_video_ids_video_results_available(self):
        expected_track_id = '1'
        expected_video_id = '2'
        spotify_playlist = {
            expected_track_id: {}
        }
        expected_search_results = ['dummy']
        expected_return_value = [{
            constants.YOUTUBE_VIDEO_ID_DATA_KEY: expected_video_id,
            constants.SEARCH_RESULTS_DATA_KEY: expected_search_results,
            constants.TRACK_POSITION_DATA_KEY: 0
        }]
        self.youtube_mock._lookup_spotify_track_on_youtube.return_value = expected_video_id, expected_search_results

        return_value = YouTube.spotify_playlist_to_video_ids(self.youtube_mock, spotify_playlist)

        self.youtube_mock._lookup_spotify_track_on_youtube.assert_called_once_with(
            spotify_playlist[expected_track_id],
            expected_track_id
        )
        self.assertEqual(return_value, expected_return_value)

    @mock.patch('youspotube.api.youtube.logging')
    def test_YouTube_dont_lookup_a_track_on_youtube_if_tied(self, logging_mock):
        expected_track_id = '1'
        tied_video_id = '2'
        track_name = 'Test'
        track_artists = ['Tester', 'Testable']
        expected_track_beautiful = Tools.get_track_string(track_name, track_artists, True)
        track = {
            'name': track_name,
            'artists': track_artists,
            'duration_ms': 1000,
        }
        expected_message = "Using tied video ID '%s' to track '%s' instead of looking it up on YouTube" % (
            tied_video_id,
            expected_track_beautiful
        )
        self.youtube_mock._get_tied_video_id_to_track_id.return_value = tied_video_id

        return_value1, return_value2 = YouTube._lookup_spotify_track_on_youtube(
            self.youtube_mock,
            track,
            expected_track_id
        )

        self.youtube_mock._get_tied_video_id_to_track_id.assert_called_once_with(expected_track_id)
        logging_mock.debug.assert_called_once_with(expected_message)
        self.assertEqual([return_value1, return_value2], [tied_video_id, None])
