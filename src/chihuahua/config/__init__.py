import ConfigParser


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
        self.config_file = config_file
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)


