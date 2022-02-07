"""Test configuration
"""
from dpres_sip_compiler.config import Config

def test_configure():
    """Test that configuration file is loaded as properties.
    """
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
    assert config.name == "Archive X"
    assert config.contract == "urn:uuid:474418c5-79a6-4e86-bfc8-5aed0a3337d7"
    assert config.sign_key == "tests/data/sign.crt"
    assert config.adaptor == "musicarchive"
    assert config.meta_ending == "___metadata.xml"
    assert config.csv_ending == "___metadata.csv"
    assert config.used_checksum == "MD5"
    assert config.desc_root_remove == "True"
