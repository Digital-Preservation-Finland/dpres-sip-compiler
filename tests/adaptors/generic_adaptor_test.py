"""Test the generic adaptor."""
from dpres_sip_compiler.adaptors.generic_adaptor import GenericFolderStructure


def test_populate():
    """Test the populate method of GenericFolderStructure.

    Test that the method collects all the filepaths in a given directory.
    """
    testclass = GenericFolderStructure()
    testclass.populate("tests/data/compiler_ng/files",
                       "tests/data/compiler_ng/generic.conf")
    assert len(testclass.premis_objects) == 2

    filepaths = get_premis_objects_filepaths(testclass.premis_objects)
    assert 'tests/data/compiler_ng/files/test_file_01.txt' in filepaths
    assert 'tests/data/compiler_ng/files/test_file_02.txt' in filepaths


def get_premis_objects_filepaths(premis_objects):
    """Helper method to collect the filepaths from a dictionary of objects.
    """
    filepaths = []
    for obj in premis_objects.values():
        path = obj.filepath
        filepaths.append(path)
    return filepaths
