"""Tests the validate module."""
from dpres_sip_compiler.validate import count_files, scrape_files


def test_scrape_files():
    """Tests the scrape_files function."""
    for file_dict in scrape_files('tests/data/musicarchive/source1/audio'):
        assert file_dict['well-formed']
        assert file_dict['grade'] == 'fi-dpres-recommended-file-format'
        assert file_dict['MIME type']
        assert file_dict['version']
        assert file_dict['tool_info']
        assert file_dict['filename']
        assert file_dict['timestamp']


def test_count_files():
    """Tests the count_files function."""
    assert count_files('tests/data/musicarchive') == 11
