"""Test CLI.
"""
# pylint: disable=protected-access

import json
import os
import shutil
import pytest
from dpres_sip_compiler.config import get_default_config_path
from dpres_sip_compiler.adaptor_list import ADAPTOR_DICT
from dpres_sip_compiler.base_adaptor import build_sip_metadata
from dpres_sip_compiler.compiler import SipCompiler


def test_compile(tmpdir, run_cli, prepare_workspace, pick_files_tar):
    """Test compile command.
    """
    (source_path, tar_file, temp_path, _) = prepare_workspace(tmpdir)
    result = run_cli(
        ["compile", "--config", "tests/data/musicarchive/config.conf",
         "--tar-file", tar_file, "--temp-path", temp_path, source_path])
    assert result.exit_code == 0

    tar_list = pick_files_tar(tar_file)
    assert "./mets.xml" in tar_list
    assert "./signature.sig" in tar_list


def test_default_config(tmpdir, run_cli, prepare_workspace, pick_files_tar):
    """Test default configuration path
    """
    (source_path, tar_file, temp_path, _) = prepare_workspace(
        tmpdir, "source1")
    conf_path = get_default_config_path()
    conf_dir = os.path.dirname(conf_path)
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    shutil.copy("tests/data/musicarchive/config.conf", conf_path)
    result = run_cli(["compile", "--tar-file", tar_file, "--temp-path",
                      temp_path, source_path])
    assert result.exit_code == 0

    tar_list = pick_files_tar(tar_file)
    assert "./mets.xml" in tar_list
    assert "./signature.sig" in tar_list


def test_clean(tmpdir, run_cli, prepare_workspace):
    """Test clean command. First create temporary files by calling
    different metadata creation steps. Eventually clean those.
    Check that only source files exist.
    """
    (source_path, _, temp_path, config) = prepare_workspace(tmpdir)
    sip_meta = build_sip_metadata(ADAPTOR_DICT, source_path, config)
    compiler = SipCompiler(source_path=source_path, temp_path=temp_path,
                           config=config, sip_meta=sip_meta)
    compiler._create_technical_metadata()
    compiler._create_provenance_metadata()
    compiler._import_descriptive_metadata()
    compiler._compile_metadata()
    result = run_cli(["clean", temp_path])
    assert result.exit_code == 0
    count = 0
    for _, _, files in os.walk(temp_path, topdown=False):
        for name in files:
            if not name.endswith(("___metadata.xml", "___metadata.csv",
                                  "testfile1.wav")):
                count = count + 1
    assert count == 0


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

    with open(valid_output) as infile:
        for line in infile:
            assert json.loads(line)['well-formed']
            supported_files_count += 1

    with open(invalid_output) as infile:
        for line in infile:
            assert not json.loads(line)['well-formed']
            unsupported_files_count += 1

    # In the used configuration, we skip files named as *___metadata.{csv,xml}
    assert supported_files_count == 6
    assert unsupported_files_count == 1

    assert os.path.isfile(
        os.path.join(str(tmpdir), 'valid_summary.jsonl')) == summary
    assert os.path.isfile(
        os.path.join(str(tmpdir), 'invalid_summary.jsonl')) == summary
