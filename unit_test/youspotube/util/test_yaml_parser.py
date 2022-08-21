import unittest
from unittest import mock

import yaml
from youspotube.exceptions import ConfigurationError
import youspotube.constants as constants
from youspotube.util.yaml_parser import YamlParser


class YamlParserTest(unittest.TestCase):
    @mock.patch('builtins.open')
    def test_YamlParser_raise_error_when_file_cannot_be_opened(self, open_mock):
        error_message = 'che yaml parserite vsichko iskat'
        open_mock.side_effect = IOError(error_message)

        with self.assertRaises(ConfigurationError) as expected_error:
            YamlParser.parse_config()

        open_mock.assert_called_once_with(constants.CONFIG_FILE_NAME, 'r')
        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Opening %s failed: %s" % (constants.CONFIG_FILE_NAME, error_message)
        )

    @mock.patch.object(yaml, 'safe_load')
    @mock.patch('builtins.open')
    def test_YamlParser_raise_error_if_type_of_file_is_not_a_dict(self, open_mock, safe_load_mock):
        safe_load_mock.return_value = []

        with self.assertRaises(ConfigurationError) as expected_error:
            YamlParser.parse_config()

        open_mock.assert_called_once_with(constants.CONFIG_FILE_NAME, 'r')
        safe_load_mock.assert_called_once_with(open_mock.return_value)
        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Content of %s should be a dictionary" % constants.CONFIG_FILE_NAME
        )

    @mock.patch.object(yaml, 'safe_load')
    @mock.patch('builtins.open')
    def test_YamlParser_raise_error_on_yaml_safe_load_failure(self, open_mock, safe_load_mock):
        expected_message = 'failed to read yaml'
        safe_load_mock.side_effect = yaml.YAMLError(expected_message)

        with self.assertRaises(ConfigurationError) as expected_error:
            YamlParser.parse_config()

        open_mock.assert_called_once_with(constants.CONFIG_FILE_NAME, 'r')
        safe_load_mock.assert_called_once_with(open_mock.return_value)
        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Parsing %s failed: %s" % (constants.CONFIG_FILE_NAME, expected_message)
        )

    @mock.patch.object(yaml, 'safe_load')
    @mock.patch('builtins.open')
    def test_YamlParser_return_parsed_yaml_config(self, open_mock, safe_load_mock):
        safe_load_mock.return_value = {}
        parsed_config = YamlParser.parse_config()

        open_mock.assert_called_once_with(constants.CONFIG_FILE_NAME, 'r')
        safe_load_mock.assert_called_once_with(open_mock.return_value)
        self.assertIs(parsed_config, safe_load_mock.return_value)
