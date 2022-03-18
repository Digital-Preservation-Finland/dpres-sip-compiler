"""Test selector.
"""
from dpres_sip_compiler.selector import select
from dpres_sip_compiler.config import Config


def test_select():
    """Test that the class is selected based on configuration.
    """
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
    sip_meta = select("tests/data/musicarchive/source1", config)
    assert sip_meta.__class__.__name__ == "SipMetadataMusicArchive"
