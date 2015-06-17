import os
import imp
from savant.util import import_string


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

    def __init__(self):
        dict.__init__(self, {})

    def from_object(self, obj):
        if isinstance(obj, str):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_envvar(self, varname, silent=False):
        var = os.environ.get(varname)
        if not var:
            if silent:
                return False
            raise RuntimeError("The envrionment variable %s is not set" % varname)
        return self.from_pyfile(var, silent=silent)

    def from_pyfile(self, filename, silent=False):
        d = imp.new_module("config")
        d.__file__ = filename
        try:
            with open(filename) as f:
                exec(compile(f.read(), filename, "exec"), d.__dict__)
        except IOError as e:
            if silent and e.errno in (errno.ENDENT, errno.EISDIR):
                return False
            e.strerror = "Unable to load configuration file (%s)" % e.strerror
            raise
        self.from_object(d)
        return True

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, dict.__repr__(self))

# The env var pre-defined
ENVIRONMENT_VARIABLE = "SAVANT_SETTINGS"
# Set up config
settings = SavantConfig()
# Read default settings
settings.from_object("savant.config.default_settings")
# Read customized settings if exists
#settings.from_envvar(ENVIRONMENT_VARIABLE)
print settings
"""
alembic_settings_file = os.path.join(os.path.dirname(__file__), "alembic.ini")
config = ConfigParser()
config.read(alembic_settings_file)
db_settings = config._sections
"""
