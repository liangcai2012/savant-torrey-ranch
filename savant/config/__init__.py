import os
from ConfigParser import ConfigParser, NoSectionError

class AttributeDictMixin(object):
    """
    Add attribute access above typical key access.
    """
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(
                '{0!r} object has no attribute {1!r}'.format(
                    type(self).__name__, k))

    def __setattr__(self, key, value):
        self[key] = value


class SavantConfig(dict, AttributeDictMixin):

    def __init__(self, silent=False):
        dict.__init__(self, {})
        self.parser = ConfigParser()
        self.config_dir = os.path.dirname(__file__)
        self.silent = silent

    def from_envvar(self, varname):
        var = os.environ.get(varname)
        if not var:
            if self.silent:
                return False
            raise RuntimeError("The envrionment variable %s is not set" % varname)
        return self.from_file(var)

    def from_file(self, config_file):
        try:
            self.parser.readfp(open(config_file))
        except IOError:
            raise

        try:
            configs = self.parser.items("SAVANT")
            for key, value in configs:
                if value.startswith("../"):
                    value = os.path.join(self.config_dir, value)
                elif value.startswith("sqlite:///.."):
                    value = value[:10] + os.path.join(self.config_dir, value[10:])
                self[key.upper()] = value.strip("\'")
        except NoSectionError:
            raise NoSectionError("No Section \'SAVANT\' in configuration file")

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, dict.__repr__(self))

# The env var pre-defined
ENVIRONMENT_VARIABLE = "SAVANT_SETTINGS"
# Set up config
settings = SavantConfig(silent=True)
# Read default settings
default_settings_file = os.path.join(os.path.split(__file__)[0],"default_settings.ini")
settings.from_file(default_settings_file)
# Read customized settings if exists
settings.from_envvar(ENVIRONMENT_VARIABLE)

alembic_settings_file = os.path.join(os.path.dirname(__file__), "alembic.ini")
config = ConfigParser()
config.read(alembic_settings_file)
db_settings = config._sections
