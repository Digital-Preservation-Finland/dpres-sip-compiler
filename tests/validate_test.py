"""Tests the validate module."""
import os
from dpres_sip_compiler.validate import (count_files, scrape_files,
                                         iterate_files)
from dpres_sip_compiler.config import Config
import pytest


def test_iterate_files(tmpdir):
    """
    Test that file exclusion feature works in file iteration.
    """
    config = Config(conf_file="tests/data/musicarchive/config.conf")

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
    config = Config(conf_file="tests/data/musicarchive/config.conf")
    for file_dict in scrape_files('tests/data/musicarchive/source1/audio',
                                  config):
        assert file_dict['well-formed']
        assert file_dict['grade'] == 'fi-dpres-recommended-file-format'
        assert file_dict['MIME type']
        assert file_dict['version']
        assert file_dict['tool_info']
        assert file_dict['filename']
        assert file_dict['timestamp']


@pytest.mark.parametrize(
    ('conf_file', 'expected_valid_files', 'expected_invalid_files'),
    [("tests/data/musicarchive/config.conf", 2, 0),
     ("tests/data/postalmuseum/postalmuseum.conf", 1, 1)]
)
def test_scrape_files_dv_concealing_errors(
        conf_file, expected_valid_files, expected_invalid_files):
    """Tests the scrape_files function with a DV file case that contains
    concealing bitstream errors only in addition to a valid file.

    Musicarchive's config should result in both files being valid.
    """
    config = Config(conf_file=conf_file)
    valid_files = 0
    invalid_files = 0
    for file_dict in scrape_files(
            'tests/data/musicarchive/conversion_dv_test_case/video/', config):
        if file_dict['well-formed']:
            valid_files += 1
        else:
            invalid_files += 1
    assert valid_files == expected_valid_files
    assert invalid_files == expected_invalid_files


def test_count_files():
    """Tests the count_files function."""
    config = Config(conf_file="tests/data/musicarchive/config.conf")
    # In the used configuration, we skip files named as *___metadata.{csv,xml}
    assert count_files('tests/data/musicarchive', config) == 18
