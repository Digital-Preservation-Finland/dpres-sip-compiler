"""Reader for configuration info
"""
import configparser


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

    @property
    def name(self):
        """Organization name"""
        return self._conf["organization"]["name"]

    @property
    def contract(self):
        """Contract identifier"""
        return self._conf["organization"]["contract"]

    @property
    def sign_key(self):
        """Path to SIP signature key"""
        return self._conf["organization"]["sign_key"]

    @property
    def module(self):
        """Module name"""
        return self._conf["script"]["module"]

    @property
    def meta_ending(self):
        """Filename ending of a metadata file"""
        return self._conf["script"]["meta_ending"]

    @property
    def used_checksum(self):
        """Checksum used for PREMIS Objects."""
        return self._conf["script"]["used_checksum"]
