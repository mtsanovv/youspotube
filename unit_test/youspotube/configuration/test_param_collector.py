import unittest
from unittest import mock

from youspotube.configuration.param_collector import CfgFileParameterCollector
import youspotube.constants as constants
from youspotube.exceptions import ConfigurationError


class CfgFileParameterCollectorTest(unittest.TestCase):
    def setUp(self):
        self.params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YOUTUBE_CLIENT_ID_PARAMETER: '',
            constants.SPOTIFY_CLIENT_ID_PARAMETER: '',
            constants.SPOTIFY_CLIENT_SECRET_PARAMETER: '',
            constants.PLAYLISTS_PARAMETER: {},
            constants.TIED_SONGS_PARAMETER: {}
        }
        self.collector = CfgFileParameterCollector(self.params)

    def test_after_CfgFileParameterCollector_instantiated(self):
        self.assertIs(self.collector.params, self.params)

    @mock.patch.object(CfgFileParameterCollector, '_copy_cfg_values')
    @mock.patch.object(CfgFileParameterCollector, '_validate_cfg')
    @mock.patch('youspotube.configuration.param_collector.YamlParser')
    def test_CfgFileParameterCollector_collect(self, yaml_parser_mock, validate_keys_mock, copy_cfg_values_mock):
        self.collector.collect()

        self.assertIs(self.collector.parsed_cfg_file, yaml_parser_mock.parse_config.return_value)
        yaml_parser_mock.parse_config.assert_called_once()
        validate_keys_mock.assert_called_once()
        copy_cfg_values_mock.assert_called_once()

    def test_CfgFileParameterCollector_cfg_validation_raise_error_when_required_param_is_missing_in_cfg_file(self):
        cfg_file_params = {
            constants.YOUTUBE_CLIENT_ID_PARAMETER: '',
            constants.SPOTIFY_CLIENT_ID_PARAMETER: '',
            constants.SPOTIFY_CLIENT_SECRET_PARAMETER: '',
            constants.PLAYLISTS_PARAMETER: {},
            constants.TIED_SONGS_PARAMETER: {}
        }
        self.collector.parsed_cfg_file = cfg_file_params

        with self.assertRaises(ConfigurationError) as expected_error:
            self.collector._validate_cfg()

        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Required parameter '%s' is missing in the configuration file" % constants.ORIGIN_PARAMETER
        )

    def test_CfgFileParameterCollector_cfg_validation__raise_error_when_required_param_is_of_different_type_in_cfg_file(self):
        cfg_file_params = {
            constants.ORIGIN_PARAMETER: 'aa',
            constants.YOUTUBE_CLIENT_ID_PARAMETER: 'dd',
            constants.SPOTIFY_CLIENT_ID_PARAMETER: 'bb',
            constants.SPOTIFY_CLIENT_SECRET_PARAMETER: 'cc',
            constants.PLAYLISTS_PARAMETER: [],
            constants.TIED_SONGS_PARAMETER: {}
        }
        self.collector.parsed_cfg_file = cfg_file_params

        with self.assertRaises(ConfigurationError) as expected_error:
            self.collector._validate_cfg()

        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Parameter '%s' is of type '%s' instead of '%s' in the configuration file" % (
                constants.PLAYLISTS_PARAMETER,
                type(cfg_file_params[constants.PLAYLISTS_PARAMETER]),
                type(self.params[constants.PLAYLISTS_PARAMETER])
            )
        )

    def test_CfgFileParameterCollector_cfg_validation_raise_error_when_required_param_has_no_value_in_cfg_file(self):
        cfg_file_params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YOUTUBE_CLIENT_ID_PARAMETER: '',
            constants.SPOTIFY_CLIENT_ID_PARAMETER: '',
            constants.SPOTIFY_CLIENT_SECRET_PARAMETER: '',
            constants.PLAYLISTS_PARAMETER: {},
            constants.TIED_SONGS_PARAMETER: {}
        }
        self.collector.parsed_cfg_file = cfg_file_params

        with self.assertRaises(ConfigurationError) as expected_error:
            self.collector._validate_cfg()

        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Parameter '%s' has an empty value in the configuration file" % constants.ORIGIN_PARAMETER
        )

    def test_CfgFileParameterCollector_copy_cfg_values(self):
        cfg_file_params = {
            constants.ORIGIN_PARAMETER: 'aa',
            constants.YOUTUBE_CLIENT_ID_PARAMETER: 'dd',
            constants.SPOTIFY_CLIENT_ID_PARAMETER: 'bb',
            constants.SPOTIFY_CLIENT_SECRET_PARAMETER: 'cc',
            constants.PLAYLISTS_PARAMETER: {'gg'},
            constants.TIED_SONGS_PARAMETER: {'ee'}
        }
        self.collector.parsed_cfg_file = cfg_file_params

        self.collector._copy_cfg_values()

        self.assertEqual(self.collector.params, cfg_file_params)
