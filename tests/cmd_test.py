"""Test CLI commands.
"""
# pylint: disable=protected-access

import json
import os
import shutil
import pytest
from dpres_sip_compiler.config import get_default_config_path


def test_compile(tmpdir, run_cli, prepare_workspace, pick_files_tar):
    """Test compile command.
    """
    (source_path, tar_file, _, _) = prepare_workspace(tmpdir)
    result = run_cli(
        ["compile", "--config", "tests/data/musicarchive/config.conf",
         "--tar-file", tar_file, source_path])
    assert result.exit_code == 0

    tar_list = pick_files_tar(tar_file)
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list


def test_default_config(tmpdir, run_cli, prepare_workspace, pick_files_tar):
    """Test default configuration path
    """
    (source_path, tar_file, _, _) = prepare_workspace(
        tmpdir, "source1")
    conf_path = get_default_config_path()
    conf_dir = os.path.dirname(conf_path)
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    shutil.copy("tests/data/musicarchive/config.conf", conf_path)
    result = run_cli(["compile", "--tar-file", tar_file, source_path])
    assert result.exit_code == 0

    tar_list = pick_files_tar(tar_file)
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list


def test_compile_options(tmpdir, run_cli, prepare_workspace, pick_files_tar):
    """Test compile command using available options.
    """
    (source_path, tar_file, _, _) = prepare_workspace(tmpdir)
    result = run_cli(
        ["compile",
         "--content-id", "Test",
         "--sip-id", "Test01",
         "--tar-file", tar_file,
         "--config", "tests/data/generic/generic.conf",
         "--no-validation",
         source_path,
         "tests/data/generic/desc_dc_metadata.xml"])
    assert result.exit_code == 0

    tar_list = pick_files_tar(tar_file)
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list


@pytest.mark.parametrize(('summary'), [
    (False),
    (True)
])
def test_validate(run_cli, tmpdir, summary):
    """Test validate command."""
    valid_output = os.path.join(str(tmpdir), 'valid.jsonl')
    invalid_output = os.path.join(str(tmpdir), 'invalid.jsonl')

    params = [
        "validate",
        "tests/data/musicarchive",
        "--valid-output", valid_output,
        "--invalid-output", invalid_output,
        "--config", "tests/data/musicarchive/config.conf"
    ]
    if summary:
        params.append("--summary")

    results = run_cli(params)
    assert results.exit_code == 0

    supported_files_count = 0
    unsupported_files_count = 0

    with open(valid_output, encoding="utf-8") as infile:
        for line in infile:
            assert json.loads(line)['well-formed']
            supported_files_count += 1

    with open(invalid_output, encoding="utf-8") as infile:
        for line in infile:
            assert not json.loads(line)['well-formed']
            unsupported_files_count += 1

    # In the used configuration, we skip files named as *___metadata.{csv,xml}
    assert supported_files_count == 13
    assert unsupported_files_count == 5

    assert os.path.isfile(
        os.path.join(str(tmpdir), 'valid_summary.jsonl')) == summary
    assert os.path.isfile(
        os.path.join(str(tmpdir), 'invalid_summary.jsonl')) == summary
