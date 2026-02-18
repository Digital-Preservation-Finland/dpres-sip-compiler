"""Test the postalmuseum adaptor."""
from dpres_sip_compiler.adaptors.postal_museum import SipMetadataPostalMuseum
from dpres_sip_compiler.config import Config


def test_populate():
    """Test the populate method of SipMetadataPostalMuseum.

    Test that the method collects all the filepaths in a given directory.
    """
    testclass = SipMetadataPostalMuseum()
    config = Config(conf_file="tests/data/postalmuseum/postalmuseum.conf")
    testclass.populate("tests/data/postalmuseum/files", config)
    assert len(testclass.premis_objects) == 2

    filepaths = _get_premis_objects_filepaths(testclass.premis_objects)
    assert 'test_file_01.txt' in filepaths
    assert 'test_file_02.txt' in filepaths


def _get_premis_objects_filepaths(premis_objects):
    """Helper method to collect the filepaths from a dictionary of objects.
    """
    filepaths = []
    for obj in premis_objects.values():
        path = obj.filepath
        filepaths.append(path)
    return filepaths


def test_descriptive_strings():
    """Test the descriptive_strings method of SipMetadataPostalMuseum.

    The XML file contains two descriptive sections.
    """
    testclass = SipMetadataPostalMuseum()
    desc_strings = []
    config = Config(conf_file="tests/data/postalmuseum/postalmuseum.conf")
    for (dataformat, desc) in testclass.descriptive_metadata_sources(
            ["tests/data/postalmuseum/lido_example_multiple_lidowraps.lido"],
            config):
        assert dataformat == 'string'
        desc_strings.append(desc)
    assert len(desc_strings) == 2
