import unittest
from unittest import mock
from unittest.mock import Mock, call

from youspotube.exceptions import ConfigurationError, ExecutionError
from youspotube.util.bootstrapper import Bootstrap
import youspotube.constants as constants
import os
from datetime import datetime
import atexit
import sys
import getpass


class BootstrapTest(unittest.TestCase):
    @mock.patch.object(ConfigurationError, 'get_exit_code', Mock(return_value=3))
    @mock.patch.object(ConfigurationError, 'print_exception')
    @mock.patch('youspotube.util.bootstrapper.Execution')
    @mock.patch('youspotube.util.bootstrapper.HttpUtil')
    @mock.patch('youspotube.util.bootstrapper.Configuration')
    def test_Bootstrap_creation_error_raised_bad_configuration(self, config_mock, httputil_mock,
                                                               execution_mock, print_exception_mock):
        expected_error = ConfigurationError('nyamame vruzka s teb sega')
        config_mock.return_value.collect_parameters.side_effect = Mock(side_effect=expected_error)

        with self.assertRaises(SystemExit) as sys_exit:
            Bootstrap()

        config_mock.assert_called_once()
        httputil_mock.check_connectivity.assert_called_once()
        config_mock.return_value.collect_parameters.assert_called_once()
        config_mock.return_value.connect_apis.assert_not_called()
        config_mock.return_value.validate_parameters.assert_not_called()
        print_exception_mock.assert_called_once()
        expected_error.get_exit_code.assert_called_once()
        self.assertEqual(sys_exit.exception.code, 3)
        execution_mock.assert_not_called()

    @mock.patch.object(ExecutionError, 'get_exit_code', Mock(return_value=3))
    @mock.patch.object(ExecutionError, 'print_exception')
    @mock.patch('youspotube.util.bootstrapper.Execution')
    @mock.patch('youspotube.util.bootstrapper.HttpUtil')
    @mock.patch('youspotube.util.bootstrapper.Configuration')
    def test_Bootstrap_creation_execution_error(self, config_mock, httputil_mock, execution_mock, print_exception_mock):
        expected_error = ExecutionError('greshka beshe')
        execution_mock.return_value.execute.side_effect = Mock(side_effect=expected_error)

        with self.assertRaises(SystemExit) as sys_exit:
            Bootstrap()

        config_mock.assert_called_once()
        httputil_mock.check_connectivity.assert_called_once()
        config_mock.return_value.collect_parameters.assert_called_once()
        config_mock.return_value.connect_apis.assert_called_once()
        config_mock.return_value.validate_parameters.assert_called_once()
        execution_mock.assert_called_once_with(config_mock.return_value)
        execution_mock.return_value.execute.assert_called_once()
        print_exception_mock.assert_called_once()
        expected_error.get_exit_code.assert_called_once()
        self.assertEqual(sys_exit.exception.code, 3)

    @mock.patch('youspotube.util.bootstrapper.sys')
    @mock.patch('youspotube.util.bootstrapper.Execution')
    @mock.patch('youspotube.util.bootstrapper.HttpUtil')
    @mock.patch('youspotube.util.bootstrapper.Configuration')
    def test_Bootstrap_creation_no_errors(self, config_mock, httputil_mock, execution_mock, sys_mock):
        Bootstrap()

        config_mock.assert_called_once()
        httputil_mock.check_connectivity.assert_called_once()
        config_mock.return_value.collect_parameters.assert_called_once()
        config_mock.return_value.connect_apis.assert_called_once()
        config_mock.return_value.validate_parameters.assert_called_once()
        execution_mock.assert_called_once_with(config_mock.return_value)
        execution_mock.return_value.execute.assert_called_once()
        sys_mock.exit.assert_not_called()

    @mock.patch.object(getpass, 'getuser')
    @mock.patch.object(atexit, 'register')
    @mock.patch.object(os, 'makedirs')
    @mock.patch('youspotube.util.bootstrapper.logging')
    def test_Bootstrap_configure_logging_not_in_unit_test_mode(self, logging_mock, makedirs_mock,
                                                               atexit_register_mock, getuser_mock):
        log_filename = constants.LOG_FILE % "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
        log_dir = os.path.join(os.getcwd(), constants.LOGS_DIR)
        log_path = os.path.join(log_dir, log_filename)

        bootstrap_mock = Mock()
        bootstrap_mock._is_in_unit_test_mode.return_value = False
        streamhandler_mock = logging_mock.StreamHandler
        filehandler_mock = logging_mock.FileHandler
        formatter_mock = logging_mock.Formatter
        expected_handlers = [streamhandler_mock.return_value, filehandler_mock.return_value]
        expected_formatter_calls = [call(constants.LOGGER_LOG_STDOUT_FORMAT), call(constants.LOGGER_LOG_FILE_FORMAT)]

        Bootstrap.configure_logging(bootstrap_mock)

        streamhandler_mock.assert_called_once_with(sys.stdout)
        formatter_mock.assert_has_calls(expected_formatter_calls)
        streamhandler_mock.return_value.setFormatter.assert_called_once_with(formatter_mock.return_value)
        streamhandler_mock.return_value.setLevel.assert_called_once_with(logging_mock.INFO)

        bootstrap_mock._is_in_unit_test_mode.assert_called_once()
        makedirs_mock.assert_called_once_with(constants.LOGS_DIR, exist_ok=True)
        filehandler_mock.assert_called_once_with(filename=log_path, mode='w', encoding='utf-8')
        filehandler_mock.return_value.setFormatter.assert_called_once_with(formatter_mock.return_value)
        filehandler_mock.return_value.setLevel.assert_called_once_with(logging_mock.DEBUG)

        logging_mock.basicConfig.assert_called_once_with(level=logging_mock.NOTSET, handlers=expected_handlers)
        atexit_register_mock.assert_called_once_with(bootstrap_mock.print_log_file_path)

        logging_mock.debug.assert_called_once_with("Running as effective user %s" % getuser_mock.return_value)

    @mock.patch.object(getpass, 'getuser')
    @mock.patch.object(atexit, 'register')
    @mock.patch.object(os, 'makedirs')
    @mock.patch('youspotube.util.bootstrapper.logging')
    def test_Bootstrap_configure_logging_in_unit_test_mode(self, logging_mock, makedirs_mock,
                                                           atexit_register_mock, getuser_mock):
        bootstrap_mock = Mock()
        bootstrap_mock._is_in_unit_test_mode.return_value = True
        streamhandler_mock = logging_mock.StreamHandler
        filehandler_mock = logging_mock.FileHandler
        formatter_mock = logging_mock.Formatter
        expected_handlers = [streamhandler_mock.return_value]

        Bootstrap.configure_logging(bootstrap_mock)

        streamhandler_mock.assert_called_once_with(sys.stdout)
        formatter_mock.assert_called_once_with(constants.LOGGER_LOG_STDOUT_FORMAT)
        streamhandler_mock.return_value.setFormatter.assert_called_once_with(formatter_mock.return_value)
        streamhandler_mock.return_value.setLevel.assert_called_once_with(logging_mock.INFO)

        bootstrap_mock._is_in_unit_test_mode.assert_called_once()
        makedirs_mock.assert_not_called()
        filehandler_mock.assert_not_called()

        logging_mock.basicConfig.assert_called_once_with(level=logging_mock.NOTSET, handlers=expected_handlers)
        atexit_register_mock.assert_called_once_with(bootstrap_mock.print_log_file_path)

        logging_mock.debug.assert_called_once_with("Running as effective user %s" % getuser_mock.return_value)

    @mock.patch('builtins.print')
    def test_Bootstrap_print_log_file_path_in_non_unit_testing_mode(self, print_mock):
        log_path = 'blargh'
        bootstrap_mock = Mock()
        bootstrap_mock._is_in_unit_test_mode.return_value = False
        bootstrap_mock.log_path = log_path

        Bootstrap.print_log_file_path(bootstrap_mock)

        print_mock.assert_called_once_with("Log file is available at '%s'" % log_path)

    @mock.patch('builtins.print')
    def test_Bootstrap_print_log_file_path_in_unit_testing_mode(self, print_mock):
        bootstrap_mock = Mock()
        bootstrap_mock._is_in_unit_test_mode.return_value = True

        Bootstrap.print_log_file_path(bootstrap_mock)

        print_mock.assert_not_called()
