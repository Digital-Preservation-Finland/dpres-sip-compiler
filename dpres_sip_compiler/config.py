import configparser


class Config(object):

    def __init__(self):
        self._conf = None

    def configure(self, conf_file):
        conf = configparser.ConfigParser()
        conf.read(conf_file)
        self._conf = conf

    @property
    def name(self):
        return self._conf["organization"]["name"]

    @property
    def contract(self):
        return self._conf["organization"]["contract"]

    @property
    def sign_key(self):
        return self._conf["organization"]["sign_key"]

    @property
    def module(self):
        return self._conf["script"]["module"]

    @property
    def meta_ending(self):
        return self._conf["script"]["meta_ending"]

    @property
    def used_checksum(self):
        return self._conf["script"]["used_checksum"]
