"""Reader for configuration info
"""
import datetime
import os
import configparser
import click

_DEFAULT_DESC_METADATA_FORMAT = "DC"
_DEFAULT_DESC_METADATA_VERSION = "2008"
_DEFAULT_DESC_METADATA_SOURCE_FORMAT = "file"
_DEFAULT_IGNORE_DV_CONCEALING_BITSTREAM_ERRORS = False


def get_default_config_path():
    """
    Get path to the default configuration file
    """
    return os.path.join(
        click.get_app_dir("dpres-sip-compiler"),
        "config.conf")


def get_default_temp_path():
    """
    Get path to the default temporary path
    """
    return os.path.join(
        os.getcwd(),
        datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%S"))


# pylint: disable=too-few-public-methods, too-many-instance-attributes
class Config:
    """Basic configuration.
    """

    def __init__(self, conf_file: str) -> None:
        """Initializes configuration.

        :param conf_file: Configuration file path
        """
        conf = configparser.ConfigParser()
        conf.read(conf_file)
        self._conf = conf

        # Organization name that will appear in METS.
        self.name = self._conf["organization"]["name"]
        # Contract ID that will appear in METS.
        self.contract = self._conf["organization"]["contract"]
        # Key that will be used to sign SIP.
        self.sign_key = self._conf["organization"]["sign_key"]

        # Which adaptor script is used.
        self.adaptor = self._conf["script"]["adaptor"]

        # Descriptive metadata's format
        try:
            _desc_metadata_format = self._conf["script"][
                "desc_metadata_format"
            ]
        except KeyError:
            _desc_metadata_format = _DEFAULT_DESC_METADATA_FORMAT
        self.desc_metadata_format = _desc_metadata_format

        # Descriptive metadata's version
        try:
            _desc_metadata_version = self._conf["script"][
                "desc_metadata_version"
            ]
        except KeyError:
            _desc_metadata_version = _DEFAULT_DESC_METADATA_VERSION
        self.desc_metadata_version = _desc_metadata_version

        # Descriptive metadata source format (i.e. "file" or "string")
        try:
            _desc_metadata_source_format = self._conf["script"][
                "desc_metadata_source_format"
            ]
        except KeyError:
            _desc_metadata_source_format = _DEFAULT_DESC_METADATA_SOURCE_FORMAT
        self.desc_metadata_source_format = _desc_metadata_source_format

        # The selected checksum in PREMIS Objects
        try:
            self.used_checksum = self._conf["script"]["used_checksum"]
        except KeyError:
            self.used_checksum = None

        # Musicarchive specific attributes.
        # Postfix part of metadata filenames
        try:
            self.meta_ending = self._conf["script"]["meta_ending"]
        except KeyError:
            self.meta_ending = None
        # Postfix part of CSV filenames.
        try:
            self.csv_ending = self._conf["script"]["csv_ending"]
        except KeyError:
            self.csv_ending = None

        try:
            self.ignore_concealing_bitstream_errors = (self._conf["validate"][
                "ignore_concealing_bitstream_errors"] == "true")
        except KeyError:
            self.ignore_concealing_bitstream_errors = (
                _DEFAULT_IGNORE_DV_CONCEALING_BITSTREAM_ERRORS)
