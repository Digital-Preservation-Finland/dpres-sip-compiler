"""Test CLI.
"""
import json
import os
import shutil
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
    for root, _, files in os.walk(temp_path, topdown=False):
        for name in files:
            if not name.endswith(("___metadata.xml", "___metadata.csv",
                                  "testfile1.wav")):
                count = count + 1
    assert count == 0


def test_validate(run_cli):
    """Test validate command."""
    results = run_cli(["validate", "tests/data/musicarchive/source1/audio"])
    assert results.exit_code == 0
    results_count = 0
    # Last result is just an empty line
    for result in results.output.split('\n')[:-1]:
        assert 'well-formed' in json.loads(result)
        results_count += 1
    assert results_count == 4
