from youspotube.util.yaml_parser import YamlParser
from youspotube.exceptions import ConfigurationError
import youspotube.constants as constants


class CfgFileParameterCollector:
    def __init__(self, params):
        self.params = params

    def collect(self):
        self.parsed_cfg_file = YamlParser.parse_config()
        self._validate_cfg()
        self._copy_cfg_values()

    def _validate_cfg(self):
        for param_name in self.params:
            if param_name not in self.parsed_cfg_file:
                raise ConfigurationError("Required parameter '%s' is missing in the configuration file" % param_name)

            config_param_type = type(self.params[param_name])
            cfg_file_param_type = type(self.parsed_cfg_file[param_name])

            if config_param_type is not cfg_file_param_type:
                raise ConfigurationError(
                    "Parameter '%s' is of type '%s' instead of '%s' in the configuration file" % (
                        param_name,
                        cfg_file_param_type,
                        config_param_type
                    )
                )

            if not self.parsed_cfg_file[param_name] and param_name not in constants.NO_DATA_EXCEPTION_PARAMETERS:
                raise ConfigurationError("Parameter '%s' has an empty value in the configuration file" % param_name)

    def _copy_cfg_values(self):
        for param_name in self.params:
            self.params[param_name] = self.parsed_cfg_file[param_name]
