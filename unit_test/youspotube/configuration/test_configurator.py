import unittest
from unittest import mock
from unittest.mock import Mock

from youspotube.configuration.configurator import Configuration
import youspotube.constants as constants

class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration()


    def test_after_Configuration_instantiated(self):
        expected_params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }
        self.assertEqual(self.configuration.params, expected_params)


    @mock.patch('youspotube.configuration.configurator.CfgFileParameterCollector')
    def test_Configuration_collect_parameters(self, cfg_file_param_collector_mock):
        expected_params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }

        self.configuration.collect_parameters()

        cfg_file_param_collector_mock.assert_called_once_with(expected_params)
        cfg_file_param_collector_mock.return_value.collect.assert_called_once()


if __name__ == '__main__':
    unittest.main()