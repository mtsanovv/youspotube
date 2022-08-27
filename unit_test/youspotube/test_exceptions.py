import unittest
from unittest import mock
from unittest.mock import Mock

from youspotube.exceptions import BaseYouspotubeError, ConfigurationError, ExecutionError
import youspotube.constants as constants

test_error_msg = 'fail'


class BaseYouspotubeErrorTest(unittest.TestCase):
    def setUp(self):
        self.exit_code = 4
        self.type = 'TestType'
        self.error = BaseYouspotubeError(test_error_msg, self.exit_code)

    def test_after_BaseYouspotubeError_instantiated(self):
        self.assertEqual(self.error.message, test_error_msg)
        self.assertEqual(self.error.exit_code, self.exit_code)

    def test_BaseYouspotubeError_to_string(self):
        expected_message = "%s error: %s" % (self.type, test_error_msg)
        self.assertEqual(self.error.__str__(self.type), expected_message)

    @mock.patch.object(BaseYouspotubeError, '__str__')
    @mock.patch('youspotube.exceptions.logging')
    def test_BaseYouspotubeError_print_exception(self, logging_mock, str_mock):
        expected_message = 'exc'
        str_mock.side_effect = Mock(return_value=expected_message)

        self.error.print_exception()

        logging_mock.critical.assert_called_once_with(expected_message)

    def test_get_exit_code_of_BaseYouspotubeError(self):
        self.assertEqual(self.error.get_exit_code(), self.exit_code)


class ConfigurationErrorTest(unittest.TestCase):
    def setUp(self):
        self.type = constants.CONFIGURATION_ERROR_TYPE
        self.error = ConfigurationError(test_error_msg)

    def test_after_ConfigurationError_instantiated(self):
        self.assertEqual(self.error.message, test_error_msg)
        self.assertEqual(self.error.exit_code, constants.EXIT_CODE_CONFIGURATION_ERROR)

    def test_ConfigurationError_to_string(self):
        expected_message = "%s error: %s" % (self.type, test_error_msg)
        self.assertEqual(self.error.__str__(), expected_message)


class ExecutionErrorTest(unittest.TestCase):
    def setUp(self):
        self.type = constants.EXECUTION_ERROR_TYPE
        self.error = ExecutionError(test_error_msg)

    def test_after_ExecutionError_instantiated_with_default_exit_code(self):
        self.assertEqual(self.error.message, test_error_msg)
        self.assertEqual(self.error.exit_code, constants.EXIT_CODE_EXECUTION_ERROR)

    def test_create_ExecutionError_with_custom_exit_code(self):
        custom_exit_code_error = ExecutionError(test_error_msg, 4)
        self.assertEqual(self.error.message, test_error_msg)
        self.assertEqual(custom_exit_code_error.exit_code, 4)

    def test_ExecutionError_to_string(self):
        expected_message = "%s error: %s" % (self.type, test_error_msg)
        self.assertEqual(self.error.__str__(), expected_message)
