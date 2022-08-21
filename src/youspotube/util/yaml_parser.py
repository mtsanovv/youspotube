import yaml
import youspotube.constants as constants
from youspotube.exceptions import ConfigurationError


class YamlParser:
    def parse_config():
        try:
            cfg_file = open(constants.CONFIG_FILE_NAME, 'r')
        except IOError as ioerr:
            raise ConfigurationError("Opening %s failed: %s" % (constants.CONFIG_FILE_NAME, ioerr))
        with cfg_file:
            try:
                cfg = yaml.safe_load(cfg_file)
                if type(cfg) is not dict:
                    raise ConfigurationError("Content of %s should be a dictionary" % constants.CONFIG_FILE_NAME)
                return cfg
            except yaml.YAMLError as ymlerr:
                raise ConfigurationError("Parsing %s failed: %s" % (constants.CONFIG_FILE_NAME, ymlerr))
