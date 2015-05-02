import os, os.path
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

    def __init__(self, config_file):
        dict.__init__(self, {})
        self.config_file = config_file
        self.parser = ConfigParser()
        self.import_config()

    def import_config(self):
        try:
            self.parser.readfp(open(self.config_file))
        except IOError:
            raise

        try:
            configs = self.parser.items("SAVANT")
            for key, value in configs:
                self[key.upper()] = value.strip("\'")
        except NoSectionError:
            raise NoSectionError("No Section \'SAVANT\' in configuration file")

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, dict.__repr__(self))


default_settings_file = os.path.join(os.path.split(__file__)[0],"default_settings.ini")
settings = SavantConfig(default_settings_file)
