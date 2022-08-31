import unittest
from unittest import mock
from unittest.mock import Mock, call

from youspotube.execution.executor import Execution
import youspotube.constants as constants
from youspotube.exceptions import ExecutionError


class ExecutionTest(unittest.TestCase):
    def setUp(self):
        self.config = Mock()
        self.spotify = self.config.get_spotify_connection.return_value
        self.youtube = self.config.get_youtube_connection.return_value

        self.playlist_names = ['Various', 'Chalga']
        self.youtube_playlists = ['ytp1', 'ytp2']
        self.spotify_playlists = ['sp1', 'sp2']

        self.tied_songs_names = ['Song1', 'Song2']
        self.youtube_tied_songs = ['ys1', 'ys2']
        self.spotify_tied_songs = ['ss1', 'ss2']

        self.params = {
            constants.PLAYLISTS_PARAMETER: {
                self.playlist_names[0]: {
                    constants.ORIGIN_YOUTUBE: self.youtube_playlists[0],
                    constants.ORIGIN_SPOTIFY: self.spotify_playlists[0]
                },
                self.playlist_names[1]: {
                    constants.ORIGIN_YOUTUBE: self.youtube_playlists[1],
                    constants.ORIGIN_SPOTIFY: self.spotify_playlists[1]
                }
            },
            constants.TIED_SONGS_PARAMETER: {
                self.tied_songs_names[0]: {
                    constants.ORIGIN_YOUTUBE: self.youtube_tied_songs[0],
                    constants.ORIGIN_SPOTIFY: self.spotify_tied_songs[0]
                },
                self.tied_songs_names[1]: {
                    constants.ORIGIN_YOUTUBE: self.youtube_tied_songs[1],
                    constants.ORIGIN_SPOTIFY: self.spotify_tied_songs[1]
                }
            }
        }

        self.config.get_params.return_value = self.params

        self.execution = Execution(self.config)

    def test_after_Execution_instantiated(self):
        self.assertIs(self.execution.config, self.config)
        self.assertIs(self.execution.params, self.params)

    @mock.patch.object(Execution, 'sync_playlists')
    @mock.patch.object(Execution, 'get_sync_direction')
    @mock.patch('youspotube.execution.executor.logging')
    def test_Execution_execute(self, logging_mock, get_sync_direction_mock, sync_playlists_mock):
        sync_direction = 'Spotify -> YouTube'
        get_sync_direction_mock.return_value = sync_direction
        expected_logging_message = "Synchronizing playlists: %s" % sync_direction

        self.execution.execute()

        logging_mock.info.assert_called_once_with(expected_logging_message)
        sync_playlists_mock.assert_called_once()

    def test_Execution_sync_direction_Spotify_to_YouTube(self):
        dashes = '-' * 10
        expected_direction_string = "Spotify %s> YouTube" % dashes
        self.params[constants.ORIGIN_PARAMETER] = constants.ORIGIN_SPOTIFY

        self.assertEqual(self.execution.get_sync_direction(), expected_direction_string)

    def test_Execution_sync_direction_YouTube_to_Spotify(self):
        dashes = '-' * 10
        expected_direction_string = "YouTube %s> Spotify" % dashes
        self.params[constants.ORIGIN_PARAMETER] = constants.ORIGIN_YOUTUBE

        self.assertEqual(self.execution.get_sync_direction(), expected_direction_string)

    @mock.patch('youspotube.execution.executor.logging')
    def test_Execution_sync_playlists_unknown_executor_origin(self, logging):
        origin = 'unknown'
        self.params[constants.ORIGIN_PARAMETER] = origin
        err_msg = "Execution error: Origin '%s', accepted by the configuration, is not recognized by the executor" % origin

        with self.assertRaises(ExecutionError) as expected_error:
            self.execution.sync_playlists()

        self.assertEqual(str(expected_error.exception), err_msg)
        logging.info.assert_not_called()

    @mock.patch.object(Execution, 'sync_from_spotify')
    @mock.patch('youspotube.execution.executor.logging')
    def test_Execution_sync_playlists_known_origin(self, logging_mock, sync_from_spotify_mock):
        self.params[constants.ORIGIN_PARAMETER] = constants.ORIGIN_SPOTIFY

        expected_info_calls = []
        expected_sync_from_spotify_calls = []
        for playlist_name in self.playlist_names:
            start_message = "Synchronizing playlist '%s' from the configuration file" % playlist_name
            end_message = "Finished synchronizing playlist '%s' from the configuration file" % playlist_name
            expected_info_calls.extend([call(start_message), call(end_message)])

            playlist_details = self.params[constants.PLAYLISTS_PARAMETER][playlist_name]
            expected_sync_from_spotify_calls.append(call(playlist_details))

        self.execution.sync_playlists()

        logging_mock.info.assert_has_calls(expected_info_calls)
        sync_from_spotify_mock.assert_has_calls(expected_sync_from_spotify_calls)

    @mock.patch.object(Execution, 'sync_from_spotify')
    @mock.patch('youspotube.execution.executor.logging')
    def test_Execution_sync_playlists_known_origin_sync_error(self, logging_mock, sync_from_spotify_mock):
        self.params[constants.ORIGIN_PARAMETER] = constants.ORIGIN_SPOTIFY
        expected_error_message = 'sync failure'
        sync_from_spotify_mock.side_effect = Exception(expected_error_message)

        expected_info_calls = []
        expected_warning_calls = []
        expected_sync_from_spotify_calls = []
        for playlist_name in self.playlist_names:
            start_message = "Synchronizing playlist '%s' from the configuration file" % playlist_name
            warning_message = "An error has occurred while synchronizing the '%s' playlist: %s" % (
                                                                                                    playlist_name,
                                                                                                    expected_error_message
                                                                                                  )
            expected_info_calls.append(call(start_message))
            expected_warning_calls.append(call(warning_message))

            playlist_details = self.params[constants.PLAYLISTS_PARAMETER][playlist_name]
            expected_sync_from_spotify_calls.append(call(playlist_details))

        self.execution.sync_playlists()

        logging_mock.info.assert_has_calls(expected_info_calls)
        sync_from_spotify_mock.assert_has_calls(expected_sync_from_spotify_calls)
        logging_mock.warning.assert_has_calls(expected_warning_calls)

    @mock.patch('youspotube.execution.executor.logging')
    def test_Execution_sync_from_spotify_nothing_to_push_to_YouTube(self, logging_mock):
        tracks_found_expected_message = "Found 2/2 Spotify tracks on YouTube"
        nothing_to_push_expected_message = "Nothing to push to YouTube playlist"
        playlist_details = self.params[constants.PLAYLISTS_PARAMETER][self.playlist_names[0]]
        ids = [1, 2]
        expected_info_calls = [call(tracks_found_expected_message), call(nothing_to_push_expected_message)]

        self.spotify.parse_playlist.return_value = ids
        self.youtube.spotify_playlist_to_video_ids.return_value = ids
        self.youtube.get_missing_videos_in_playlist.return_value = []

        self.execution.sync_from_spotify(playlist_details)

        self.spotify.parse_playlist.assert_called_once_with(playlist_details)
        self.youtube.spotify_playlist_to_video_ids.assert_called_once_with(ids)
        self.youtube.get_missing_videos_in_playlist.assert_called_once_with(playlist_details, ids)
        logging_mock.info.assert_has_calls(expected_info_calls)

    @mock.patch('youspotube.execution.executor.logging')
    def test_Execution_sync_from_spotify_push_to_YouTube(self, logging_mock):
        tracks_found_expected_message = "Found 2/2 Spotify tracks on YouTube"
        expected_pushing_message = "Pushing 2 videos to YouTube playlist that are not in it"
        playlist_details = self.params[constants.PLAYLISTS_PARAMETER][self.playlist_names[0]]
        ids = [1, 2]
        expected_info_calls = [call(tracks_found_expected_message), call(expected_pushing_message)]

        self.spotify.parse_playlist.return_value = ids
        self.youtube.spotify_playlist_to_video_ids.return_value = ids
        self.youtube.get_missing_videos_in_playlist.return_value = ids

        self.execution.sync_from_spotify(playlist_details)

        self.spotify.parse_playlist.assert_called_once_with(playlist_details)
        self.youtube.spotify_playlist_to_video_ids.assert_called_once_with(ids)
        self.youtube.get_missing_videos_in_playlist.assert_called_once_with(playlist_details, ids)
        logging_mock.info.assert_has_calls(expected_info_calls)
        self.youtube.add_videos_to_playlist.assert_called_once_with(playlist_details, ids)

    @mock.patch('youspotube.execution.executor.logging')
    def test_Execution_sync_from_YouTube_nothing_to_push_to_Spotify(self, logging_mock):
        tracks_found_expected_message = "Found 2/2 YouTube songs on Spotify"
        nothing_to_push_expected_message = "Nothing to push to Spotify playlist"
        playlist_details = self.params[constants.PLAYLISTS_PARAMETER][self.playlist_names[0]]
        ids = [1, 2]
        expected_info_calls = [call(tracks_found_expected_message), call(nothing_to_push_expected_message)]

        self.youtube.parse_playlist.return_value = ids
        self.spotify.youtube_playlist_to_track_ids.return_value = ids
        self.youtube.get_relevant_spotify_tracks.return_value = ids
        self.spotify.get_missing_tracks_in_playlist.return_value = []

        self.execution.sync_from_youtube(playlist_details)

        self.youtube.parse_playlist.assert_called_once_with(playlist_details)
        self.spotify.youtube_playlist_to_track_ids.assert_called_once_with(ids)
        self.youtube.get_relevant_spotify_tracks.assert_called_once_with(ids)
        self.spotify.get_missing_tracks_in_playlist.assert_called_once_with(playlist_details, ids)
        logging_mock.info.assert_has_calls(expected_info_calls)

    @mock.patch('youspotube.execution.executor.logging')
    def test_Execution_sync_from_YouTube_push_to_Spotify(self, logging_mock):
        tracks_found_expected_message = "Found 2/2 YouTube songs on Spotify"
        expected_pushing_message = "Pushing 2 tracks to Spotify playlist that are not in it"
        playlist_details = self.params[constants.PLAYLISTS_PARAMETER][self.playlist_names[0]]
        ids = [1, 2]
        expected_info_calls = [call(tracks_found_expected_message), call(expected_pushing_message)]

        self.youtube.parse_playlist.return_value = ids
        self.spotify.youtube_playlist_to_track_ids.return_value = ids
        self.youtube.get_relevant_spotify_tracks.return_value = ids
        self.spotify.get_missing_tracks_in_playlist.return_value = ids

        self.execution.sync_from_youtube(playlist_details)

        self.youtube.parse_playlist.assert_called_once_with(playlist_details)
        self.spotify.youtube_playlist_to_track_ids.assert_called_once_with(ids)
        self.youtube.get_relevant_spotify_tracks.assert_called_once_with(ids)
        self.spotify.get_missing_tracks_in_playlist.assert_called_once_with(playlist_details, ids)
        logging_mock.info.assert_has_calls(expected_info_calls)
        self.spotify.add_tracks_to_playlist.assert_called_once_with(playlist_details, ids)
