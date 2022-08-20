import unittest
from unittest import mock

import sys
from youspotube.configuration.argv import ArgvParser
from youspotube.exceptions import ConfigurationError
import youspotube.constants as constants

class ArgvParserTest(unittest.TestCase):
    @mock.patch.object(sys, 'argv', ['executable', constants.HELP_OPTION, 'a'])
    def test_create_ArgvParser_with_more_than_two_argv_and_help_requested(self):
        with self.assertRaises(ConfigurationError) as config_err:
            argv_parser = ArgvParser()
            self.assertEqual(argv_parser.argv_count, 3)
            self.assertEqual(argv_parser.is_help(), True)
            self.assertEqual(argv_parser.should_use_cfg_file(), False)
        expected_config_err_msg = "Configuration error: No other arguments should be passed to the program when the %s option is passed" % constants.HELP_OPTION
        self.assertEqual(str(config_err.exception), expected_config_err_msg)


    @mock.patch.object(sys, 'argv', ['executable', constants.HELP_OPTION])
    def test_create_ArgvParser_with_two_argv_and_help_requested(self):
        argv_parser = ArgvParser()
        self.assertEqual(argv_parser.argv_count, 2)
        self.assertEqual(argv_parser.is_help(), True)
        self.assertEqual(argv_parser.should_use_cfg_file(), False)


    @mock.patch.object(sys, 'argv', ['executable', constants.CONFIG_FILE_OPTION, 'a'])
    def test_create_ArgvParser_with_more_than_two_argv_and_cfg_file_to_be_used(self):
        with self.assertRaises(ConfigurationError) as config_err:
            argv_parser = ArgvParser()
            self.assertEqual(argv_parser.argv_count, 3)
            self.assertEqual(argv_parser.is_help(), False)
            self.assertEqual(argv_parser.should_use_cfg_file(), True)
        expected_config_err_msg = "Configuration error: No other arguments should be passed to the program when the %s option is passed" % constants.CONFIG_FILE_OPTION
        self.assertEqual(str(config_err.exception), expected_config_err_msg)


    @mock.patch.object(sys, 'argv', ['executable', 'aaa', 'bbb'])
    def test_create_ArgvParser_with_less_than_six_argv_no_help_no_cfg_file_to_be_used(self):
        with self.assertRaises(ConfigurationError) as config_err:
            argv_parser = ArgvParser()
            self.assertEqual(argv_parser.argv_count, 3)
            self.assertEqual(argv_parser.is_help(), False)
            self.assertEqual(argv_parser.should_use_cfg_file(), False)
        expected_config_err_msg = "Configuration error: Command line arguments should be at least six when %s and %s are not specified - run %s %s to see the correct usage" % (constants.HELP_OPTION, constants.CONFIG_FILE_OPTION, 'executable', constants.HELP_OPTION)
        self.assertEqual(str(config_err.exception), expected_config_err_msg)


    @mock.patch.object(sys, 'argv', ['executable', 1, 2, 3, 4, 5])
    def test_create_ArgvParser_with_six_argv_no_help_no_cfg_file_to_be_used(self):
        argv_parser = ArgvParser()
        self.assertEqual(argv_parser.argv_count, 6)
        self.assertEqual(argv_parser.is_help(), False)
        self.assertEqual(argv_parser.should_use_cfg_file(), False)

    @mock.patch.object(sys, 'argv', ['executable', 1, 2, 3, 4, 5])
    def test_ArgvParser_create_no_more_arguments_error_message(self):
        argv_parser = ArgvParser()
        option = '-test'
        expected_error_message = "No other arguments should be passed to the program when the %s option is passed" % option
        self.assertEqual(argv_parser._get_no_more_arguments_error_message(option), expected_error_message)


    @mock.patch.object(sys, 'argv', ['executable', 'origin', 'token1', 'token2', 'playlist1', 'playlist2', 'playlist3'])
    def test_ArgvParser_collect_seven_cmd_line_params(self):
        argv_parser = ArgvParser()
        params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }
        expected_params = {
            constants.ORIGIN_PARAMETER: 'origin',
            constants.YT_TOKEN_PARAMETER: 'token1',
            constants.SPOTIFY_TOKEN_PARAMETER: 'token2',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }

        with self.assertRaises(ConfigurationError) as config_error:
            argv_parser.collect_cmd_line_params(params)

        self.assertEqual(str(config_error.exception), "Configuration error: Command line arguments should be an even number - are you missing a Spotify or a YouTube playlist ID?")
        self.assertEqual(params, expected_params)


    @mock.patch.object(sys, 'argv', ['executable', 'origin', 'token1', 'token2', 'playlist1', 'playlist2', 'playlist3', 'playlist4'])
    def test_ArgvParser_collect_eight_cmd_line_params(self):
        argv_parser = ArgvParser()
        params = {
            constants.ORIGIN_PARAMETER: '',
            constants.YT_TOKEN_PARAMETER: '',
            constants.SPOTIFY_TOKEN_PARAMETER: '',
            constants.YT_PLAYLISTS_PARAMETER: [],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: []
        }
        expected_params = {
            constants.ORIGIN_PARAMETER: 'origin',
            constants.YT_TOKEN_PARAMETER: 'token1',
            constants.SPOTIFY_TOKEN_PARAMETER: 'token2',
            constants.YT_PLAYLISTS_PARAMETER: ['playlist1', 'playlist3'],
            constants.SPOTIFY_PLAYLISTS_PARAMETER: ['playlist2', 'playlist4']
        }

        argv_parser.collect_cmd_line_params(params)

        self.assertEqual(params, expected_params)


if __name__ == '__main__':
    unittest.main()