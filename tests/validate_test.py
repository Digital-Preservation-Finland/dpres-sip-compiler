"""Tests the validate module."""
import os
from dpres_sip_compiler.validate import (count_files, scrape_files,
                                         iterate_files)
from dpres_sip_compiler.config import Config


def test_iterate_files(tmpdir):
    """
    Test that file exclusion feature works in file iteration.
    """
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")

    count = 0
    count_real = 0

    tmp_path = str(tmpdir)
    hidden = os.path.join(tmp_path, ".hidden_file")
    open(hidden, "w").close()
    assert os.path.isfile(hidden)

    for _ in iterate_files(tmp_path, config):
        count += 1
    for _ in os.walk(tmp_path):
        count_real += 1

    assert count == 0
    assert count_real == 1


def test_scrape_files():
    """Tests the scrape_files function."""
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
    for file_dict in scrape_files('tests/data/musicarchive/source1/audio',
                                  config):
        assert file_dict['well-formed']
        assert file_dict['grade'] == 'fi-dpres-recommended-file-format'
        assert file_dict['MIME type']
        assert file_dict['version']
        assert file_dict['tool_info']
        assert file_dict['filename']
        assert file_dict['timestamp']


def test_count_files():
    """Tests the count_files function."""
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
    # In the used configuration, we skip files named as *___metadata.{csv,xml}
    assert count_files('tests/data/musicarchive', config) == 14
