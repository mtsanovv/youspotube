import unittest
from unittest import mock

from youspotube.configuration.param_validator import ParameterValidator
import youspotube.constants as constants
from youspotube.exceptions import ConfigurationError


class ParameterValidatorTest(unittest.TestCase):
    def setUp(self):
        self.params = {
            constants.ORIGIN_PARAMETER: 'aa',
            constants.YT_TOKEN_PARAMETER: 'cc',
            constants.SPOTIFY_CLIENT_ID_PARAMETER: 'bb',
            constants.SPOTIFY_CLIENT_SECRET_PARAMETER: 'dd',
            constants.PLAYLISTS_PARAMETER: {},
            constants.TIED_SONGS_PARAMETER: {}
        }
        self.validator = ParameterValidator(self.params)

    def test_ParameterValidator_after_instantiated(self):
        self.assertIs(self.validator.params, self.params)

    @mock.patch.object(ParameterValidator, "%s%s" % (constants.CHECK_PARAM_METHOD_PREFIX, constants.TIED_SONGS_PARAMETER))
    @mock.patch.object(ParameterValidator, "%s%s" % (constants.CHECK_PARAM_METHOD_PREFIX, constants.PLAYLISTS_PARAMETER))
    @mock.patch.object(ParameterValidator, "%s%s" % (constants.CHECK_PARAM_METHOD_PREFIX, constants.ORIGIN_PARAMETER))
    def test_ParameterValidator_call_check_params_methods(self, check_origin_mock, check_playlists_mock, tied_songs_mock):
        self.validator.check_params()

        check_origin_mock.assert_called_once_with(self.params[constants.ORIGIN_PARAMETER])
        check_playlists_mock.assert_called_once_with(self.params[constants.PLAYLISTS_PARAMETER])
        tied_songs_mock.assert_called_once_with(self.params[constants.TIED_SONGS_PARAMETER])

    def test_ParameterValidator_raise_error_on_bad_origin(self):
        bad_origin = 'bad'
        with self.assertRaises(ConfigurationError) as expected_error:
            self.validator.check_origin(bad_origin)

        self.assertEquals(
            str(expected_error.exception),
            "Configuration error: Unknown origin set in the configuration file: '%s'. Use one of the following: %s" % (
                bad_origin,
                ', '.join(constants.ORIGINS)
            )
        )

    def test_ParameterValidator_no_error_with_accepted_origin(self):
        self.validator.check_origin(constants.ORIGINS[0])

    def test_ParameterValidator_raise_error_on_playlist_that_contains_required_field_that_is_not_a_string(self):
        dict_type = 'tied song'
        playlist = {
            'youtube': 1,
            'spotify': 'aa'
        }
        playlist_name = 'Favorite Music'

        with self.assertRaises(ConfigurationError) as expected_error:
            self.validator.check_song_playlist_keys(playlist, playlist_name, dict_type)

        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Required field 'youtube' of %s '%s' is not a string in the configuration file" % (
                dict_type,
                playlist_name
            )
        )

    def test_ParameterValidator_raise_error_on_playlist_that_contains_no_value_for_a_required_field(self):
        dict_type = 'playlist'
        playlist = {
            'youtube': 'bb',
            'spotify': ''
        }
        playlist_name = 'Favorite Music'

        with self.assertRaises(ConfigurationError) as expected_error:
            self.validator.check_song_playlist_keys(playlist, playlist_name, dict_type)

        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: There's no value for the required field 'spotify' of %s '%s' in the configuration file" % (
                dict_type,
                playlist_name
            )
        )

    def test_ParameterValidator_no_error_on_playlist_that_contains_acceptable_values(self):
        dict_type = 'playlist'
        playlist = {
            'youtube': 'bb',
            'spotify': 'cc'
        }
        playlist_name = 'Favorite Music'

        self.validator.check_song_playlist_keys(playlist, playlist_name, dict_type)

    @mock.patch.object(ParameterValidator, 'check_song_playlist_keys')
    def test_ParameterValidator_raise_error_if_playlist_is_not_a_dict(self, check_song_playlist_keys_mock):
        dict_type = 'playlist'
        playlists = {
            'Chalga': []
        }

        with self.assertRaises(ConfigurationError) as expected_error:
            self.validator.check_song_playlist(playlists, dict_type)

        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Playlist 'Chalga' is not a dictionary in the configuration file"
        )
        check_song_playlist_keys_mock.assert_not_called()

    @mock.patch.object(ParameterValidator, 'check_song_playlist_keys')
    def test_ParameterValidator_raise_error_if_required_field_not_in_tied_song(self, check_song_playlist_keys_mock):
        dict_type = 'tied song'
        playlists = {
            'Chalga': {
                'youtube': 'something'
            }
        }

        with self.assertRaises(ConfigurationError) as expected_error:
            self.validator.check_song_playlist(playlists, dict_type)

        self.assertEqual(
            str(expected_error.exception),
            "Configuration error: Tied song 'Chalga' does not contain the required field 'spotify' in the configuration file"
        )
        check_song_playlist_keys_mock.assert_not_called()

    @mock.patch.object(ParameterValidator, 'check_song_playlist_keys')
    def test_ParameterValidator_no_error_on_acceptable_playlists_collection(self, check_song_playlist_keys_mock):
        dict_type = 'playlist'
        nested_playlist_name = 'Chalga'
        nested_playlist = {
            'youtube': 'bb',
            'spotify': 'cc'
        }
        playlists = {
            nested_playlist_name: nested_playlist
        }

        self.validator.check_song_playlist(playlists, dict_type)

        check_song_playlist_keys_mock.assert_called_once_with(nested_playlist, nested_playlist_name, dict_type)

    @mock.patch.object(ParameterValidator, 'check_song_playlist')
    def test_ParameterValidator_check_playlists(self, check_song_playlist_mock):
        playlists = {}

        self.validator.check_playlists(playlists)

        check_song_playlist_mock.assert_called_once_with(playlists, 'playlist')

    @mock.patch.object(ParameterValidator, 'check_song_playlist')
    def test_ParameterValidator_do_not_check_tied_songs_if_there_are_none(self, check_song_playlist_mock):
        self.validator.check_tied_songs({})

        check_song_playlist_mock.assert_not_called()

    @mock.patch.object(ParameterValidator, 'check_song_playlist')
    def test_ParameterValidator_check_tied_songs(self, check_song_playlist_mock):
        tied_songs = {
            'DesiSlava - Toxic': {
                'youtube': 'aa',
                'spotify': 'bb'
            }
        }

        self.validator.check_tied_songs(tied_songs)

        check_song_playlist_mock.assert_called_once_with(tied_songs, 'tied song')
