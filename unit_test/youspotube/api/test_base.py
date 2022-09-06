import unittest
from unittest.mock import Mock

from youspotube.api.base import BaseAPI
from youspotube.exceptions import ConfigurationError


class BaseAPITest(unittest.TestCase):
    def setUp(self):
        self.base_mock = Mock()

    def test_BaseAPI_creation_no_error(self):
        expected_client_id = 1
        expected_client_secret = 2
        expected_tied_songs = {}

        BaseAPI.__init__(self.base_mock, expected_client_id, expected_client_secret, expected_tied_songs)

        self.assertEqual(expected_client_id, self.base_mock.client_id)
        self.assertEqual(expected_client_secret, self.base_mock.client_secret)
        self.assertIs(expected_tied_songs, self.base_mock.tied_songs)
        self.base_mock._init_connection.assert_called_once()
        self.base_mock._test_connection.assert_called_once()

    def test_Spotify_creation_error(self):
        expected_client_id = 1
        expected_client_secret = 2
        expected_tied_songs = {}
        error_reason = 'bad api'
        expected_error_message = "Configuration error: Test connection to Mock API failed: %s" % error_reason
        self.base_mock._init_connection.side_effect = Exception(error_reason)

        with self.assertRaises(ConfigurationError) as expected_error:
            BaseAPI.__init__(self.base_mock, expected_client_id, expected_client_secret, expected_tied_songs)

        self.assertEqual(expected_client_id, self.base_mock.client_id)
        self.assertEqual(expected_client_secret, self.base_mock.client_secret)
        self.assertIs(expected_tied_songs, self.base_mock.tied_songs)
        self.assertEqual(str(expected_error.exception), expected_error_message)
        self.base_mock._init_connection.assert_called_once()
        self.base_mock._test_connection.assert_not_called()
