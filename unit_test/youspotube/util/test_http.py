import unittest
from unittest import mock
from unittest.mock import call

from youspotube.exceptions import ConfigurationError
from youspotube.util.http import HttpUtil
import youspotube.constants as constants


class HttpUtilTest(unittest.TestCase):
    @mock.patch.object(HttpUtil, '_check_url')
    def test_HttpUtil_check_connectivity_raise_error_if_url_check_raises_exception(self, check_url_mock):
        expected_message = 'spryah li ti neta'
        check_url_mock.side_effect = Exception(expected_message)

        with self.assertRaises(ConfigurationError) as config_err:
            HttpUtil.check_connectivity()

        check_url_mock.assert_called_once_with(constants.SPOTIFY_API_URL)
        self.assertEqual(
            str(config_err.exception),
            "Configuration error: Failed to connect to %s: %s" % (constants.SPOTIFY_API_URL, expected_message)
        )

    @mock.patch.object(HttpUtil, '_check_url')
    def test_HttpUtil_check_connectivity_no_error(self, check_url_mock):
        expected_calls = [call(constants.SPOTIFY_API_URL), call(constants.YOUTUBE_API_URL)]

        HttpUtil.check_connectivity()

        check_url_mock.assert_has_calls(expected_calls)

    @mock.patch('youspotube.util.http.requests')
    def test_HttpUtil_check_url(self, requests_mock):
        test_url = 'http://nedeljko.bajic.baja'

        HttpUtil._check_url(test_url)

        requests_mock.head.assert_called_with(test_url)
