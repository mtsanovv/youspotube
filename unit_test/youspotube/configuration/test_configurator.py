import unittest
from unittest import mock
from unittest.mock import Mock

from youspotube.configuration.configurator import Configuration, CollectorFactory
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
        self.assertEqual(self.configuration.is_help, False)
        self.assertEqual(self.configuration.params, expected_params)


    @mock.patch('youspotube.configuration.configurator.CollectorFactory')
    @mock.patch('youspotube.configuration.configurator.ArgvParser')
    def test_Configuration_do_not_collect_parameter_if_help_is_requested(self, argv_parser_mock, collector_factory_mock):
        argv_parser_mock.return_value.is_help.return_value = True

        self.configuration.collect_parameters()

        argv_parser_mock.return_value.is_help.assert_called_once()
        self.assertEqual(self.configuration.is_help, True)
        collector_factory_mock._create_collector.assert_not_called()


    @mock.patch('youspotube.configuration.configurator.CollectorFactory')
    @mock.patch('youspotube.configuration.configurator.ArgvParser')
    def test_Configuration_should_call_CollectorFactory_to_collect_parameters_if_help_is_not_requested(self, argv_parser_mock, collector_factory_mock):
        collector_mock = Mock()
        expected_params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }
        argv_parser_mock.return_value.is_help.return_value = False
        argv_parser_mock.return_value.should_use_cfg_file.return_value = False
        collector_factory_mock._create_collector.return_value = collector_mock

        self.configuration.collect_parameters()

        argv_parser_mock.return_value.is_help.assert_called_once()
        argv_parser_mock.return_value.should_use_cfg_file.assert_called_once()
        self.assertEqual(self.configuration.is_help, False)
        collector_factory_mock._create_collector.assert_called_once_with(expected_params, False)
        collector_mock.collect.assert_called_once()


    def test_Configuration_check_help_requested(self):
        self.assertEqual(self.configuration.is_help_requested(), False)


    def test_Configuration_get_params(self):
        expected_params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }

        self.assertEqual(self.configuration.get_params(), expected_params)


class CollectorFactoryTest(unittest.TestCase):
    @mock.patch('youspotube.configuration.configurator.CfgFileParameterCollector')
    @mock.patch('youspotube.configuration.configurator.CmdLineParameterCollector')
    def test_CollectorFactory_create_config_file_collector_if_config_file_should_be_used_for_parameter_configuration(self, cmd_line_param_collector_mock, cfg_file_param_collector_mock):
        expected_params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }

        CollectorFactory._create_collector(expected_params, True)

        cfg_file_param_collector_mock.assert_called_once_with(expected_params)
        cmd_line_param_collector_mock.assert_not_called()


    @mock.patch('youspotube.configuration.configurator.CfgFileParameterCollector')
    @mock.patch('youspotube.configuration.configurator.CmdLineParameterCollector')
    def test_CollectorFactory_create_cmd_line_parameter_collector_if_config_file_should_not_be_used_for_parameter_configuration(self, cmd_line_param_collector_mock, cfg_file_param_collector_mock):
        expected_params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }

        CollectorFactory._create_collector(expected_params, False)

        cfg_file_param_collector_mock.assert_not_called()
        cmd_line_param_collector_mock.assert_called_once_with(expected_params)


if __name__ == '__main__':
    unittest.main()