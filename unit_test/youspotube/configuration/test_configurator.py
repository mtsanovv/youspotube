import unittest
from unittest import mock
from unittest.mock import Mock

from youspotube.configuration.configurator import Configuration
import youspotube.constants as constants


class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_CLIENT_ID_PARAMETER: '',
            constants.SPOTIFY_CLIENT_SECRET_PARAMETER: '',
            constants.PLAYLISTS_PARAMETER: {},
            constants.TIED_SONGS_PARAMETER: {}
        }
        self.configuration = Configuration()

    def test_after_Configuration_instantiated(self):
        self.assertEqual(self.configuration.params, self.params)

    @mock.patch('youspotube.configuration.configurator.CfgFileParameterCollector')
    def test_Configuration_collect_parameters(self, cfg_file_param_collector_mock):
        self.configuration.collect_parameters()

        cfg_file_param_collector_mock.assert_called_once_with(self.params)
        cfg_file_param_collector_mock.return_value.collect.assert_called_once()

    @mock.patch('youspotube.configuration.configurator.ParameterValidator')
    def test_Configuration_validate_parameters(self, validator_mock):
        self.configuration.validate_parameters()

        validator_mock.assert_called_once_with(self.params)
        validator_mock.return_value.check_params.assert_called_once()

    @mock.patch('youspotube.configuration.configurator.YouTube')
    @mock.patch('youspotube.configuration.configurator.Spotify')
    def test_Configuration_connect_apis(self, spotify_mock, youtube_mock):
        expected_spotify_client_id = 'aa'
        expected_spotify_secret = 'bb'
        expected_youtube_token = 'cc'
        self.configuration.params[constants.SPOTIFY_CLIENT_ID_PARAMETER] = expected_spotify_client_id
        self.configuration.params[constants.SPOTIFY_CLIENT_SECRET_PARAMETER] = expected_spotify_secret
        self.configuration.params[constants.YT_TOKEN_PARAMETER] = expected_youtube_token

        self.configuration.connect_apis()

        spotify_mock.assert_called_once_with(expected_spotify_client_id, expected_spotify_secret)
        youtube_mock.assert_called_once_with(expected_youtube_token)
        self.assertIs(self.configuration.spotify_connection, spotify_mock.return_value)
        self.assertIs(self.configuration.youtube_connection, youtube_mock.return_value)

    def test_Configuration_get_params(self):
        self.assertEqual(self.configuration.get_params(), self.params)

    def test_Configuration_get_spotify_connection(self):
        spotify_connection = Mock()
        self.configuration.spotify_connection = spotify_connection
        self.assertIs(self.configuration.get_spotify_conenction(), spotify_connection)

    def test_Configuration_get_youtube_connection(self):
        youtube_connection = Mock()
        self.configuration.youtube_connection = youtube_connection
        self.assertIs(self.configuration.get_youtube_connection(), youtube_connection)
