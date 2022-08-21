import unittest
from unittest import mock
from unittest.mock import Mock

from youspotube.exceptions import ConfigurationError, ExecutionError
from youspotube.util.bootstrapper import Bootstrap


class BootstrapTest(unittest.TestCase):
    @mock.patch.object(ConfigurationError, 'get_exit_code', Mock(return_value=3))
    @mock.patch.object(ConfigurationError, 'print_exception')
    @mock.patch('youspotube.util.bootstrapper.Execution')
    @mock.patch('youspotube.util.bootstrapper.HttpUtil')
    @mock.patch('youspotube.util.bootstrapper.Configuration')
    def test_Bootstrap_creation_error_raised_bad_configuration(self, config_mock, httputil_mock,
                                                               execution_mock, print_exception_mock):
        expected_error = ConfigurationError('nyamame vruzka s teb sega')
        config_mock.return_value.connect_apis.side_effect = Mock(side_effect=expected_error)

        with self.assertRaises(SystemExit) as sys_exit:
            Bootstrap()

        config_mock.assert_called_once()
        httputil_mock.check_connectivity.assert_called_once()
        config_mock.return_value.collect_parameters.assert_called_once()
        config_mock.return_value.connect_apis.assert_called_once()
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
        execution_mock.assert_called_once_with(config_mock.return_value)
        execution_mock.return_value.execute.assert_called_once()
        sys_mock.exit.assert_not_called()
