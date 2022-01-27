"""Reader for configuration info
"""
import configparser
import six


class Config(object):
    """Basic configuration.
    """

    def __init__(self):
        """Initialize"""
        self._conf = None

    def configure(self, conf_file):
        """Read configuration.
        :conf_file: Configuration file path
        """
        conf = configparser.ConfigParser()
        conf.read(conf_file)
        self._conf = conf

    def __getattr__(self, attr):
        """
        Set script configuration items as properties.
        :attr: Attribute name
        :returns: Value for given attribute
        :raises: AttributeError if does not exist.
        """
        try:
            if attr in self._conf["organization"]:
                return self._conf["organization"][attr]

            return self._conf["script"][attr]
        except Exception as exception:
            raise AttributeError(six.text_type(exception))
