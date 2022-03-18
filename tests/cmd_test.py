"""Test CLI.
"""
import os
import shutil
from dpres_sip_compiler.config import get_default_config_path
from dpres_sip_compiler.selector import select
from dpres_sip_compiler.compiler import SipCompiler


def test_compile(tmpdir, run_cli, prepare_workspace):
    """Test compile command.
    """
    (source_path, tar_file, temp_path, _) = prepare_workspace(
        tmpdir, "source1")
    result = run_cli(
        ["compile", "--config", "tests/data/musicarchive/config.conf",
         "--tar-file", tar_file, "--temp-path", temp_path, source_path])
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(temp_path, "mets.xml"))
    assert os.path.isfile(os.path.join(temp_path, "signature.sig"))
    assert os.path.isfile(os.path.join(tar_file))


def test_default_config(tmpdir, run_cli, prepare_workspace):
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
    assert os.path.isfile(os.path.join(temp_path, "mets.xml"))
    assert os.path.isfile(os.path.join(temp_path, "signature.sig"))
    assert os.path.isfile(os.path.join(tar_file))


def test_clean(tmpdir, run_cli, prepare_workspace):
    """Test clean command. First create temporary files by calling
    different metadata creation steps. Eventually clean those.
    Check that only source files exist.
    """
    (source_path, _, temp_path, config) = prepare_workspace(tmpdir)
    sip_meta = select(source_path, config)
    compiler = SipCompiler(source_path, None, temp_path, config, sip_meta)
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
