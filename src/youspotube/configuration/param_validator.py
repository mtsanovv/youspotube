from tabnanny import check
import youspotube.constants as constants
from youspotube.exceptions import ConfigurationError


class ParameterValidator:
    def __init__(self, params):
        self.params = params

    def check_params(self):
        for param_name in self.params:
            check_method = "%s%s" % (constants.CHECK_PARAM_METHOD_PREFIX, param_name)
            if hasattr(self, check_method):
                getattr(self, check_method)(self.params[param_name])

    def check_origin(self, origin):
        if origin not in constants.ORIGINS:
            raise ConfigurationError("Unknown origin set in the configuration file: '%s'. Use one of the following: %s" % (origin, ', '.join(constants.ORIGINS)))

    def check_song_playlist_keys(self, dict, dict_name, dict_type):
        for required_key in constants.REQUIRED_KEYS_PLAYLISTS_SONGS:
            if type(dict[required_key]) is not str:
                raise ConfigurationError("Required field '%s' of %s '%s' is not a string in the configuration file" % (required_key, dict_type, dict_name))
            if not dict[required_key]:
                raise ConfigurationError("There's no value for the required field '%s' of %s '%s' in the configuration file" % (required_key, dict_type, dict_name))

    def check_song_playlist(self, dictionary, dict_type):
        dict_type_capitalized = dict_type.capitalize()
        for key_name in dictionary:
            nested_dict = dictionary[key_name]
            if type(nested_dict) is not dict:
                raise ConfigurationError("%s '%s' is not a dictionary in the configuration file" % (dict_type_capitalized, key_name))
            for required_field in constants.REQUIRED_KEYS_PLAYLISTS_SONGS:
                if required_field not in nested_dict:
                    raise ConfigurationError("%s '%s' does not contain the required field '%s' in the configuration file" % (dict_type_capitalized, key_name, required_field))
            self.check_song_playlist_keys(nested_dict, key_name, dict_type)

    def check_playlists(self, playlists):
        self.check_song_playlist(playlists, 'playlist')

    def check_tied_songs(self, tied_songs):
        if not tied_songs:
            return
        self.check_song_playlist(tied_songs, 'tied song')
