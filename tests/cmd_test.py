"""Test CLI.
"""
import os
from siptools.scripts.compile_structmap import compile_structmap
from dpres_sip_compiler.selector import select
from dpres_sip_compiler.compiler import SipCompiler


def test_compile(tmpdir, run_cli, prepare_workspace):
    """Test compile command.
    """
    (workspace, _) = prepare_workspace(tmpdir, "workspace1")
    result = run_cli(["compile", "tests/data/musicarchive/config.conf",
                      workspace])
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(workspace, "mets.xml"))
    assert os.path.isfile(os.path.join(workspace, "signature.sig"))
    assert os.path.isfile(os.path.join(workspace,
                                       "Package_2022_02_07_123.tar"))


def test_clean(tmpdir, run_cli, prepare_workspace):
    """Test clean command.
    """
    (workspace, config) = prepare_workspace(tmpdir)
    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace, config, sip_meta)
    compiler._technical_metadata()
    compiler._provenance_metadata()
    compiler._descriptive_metadata()
    compile_structmap(workspace)
    result = run_cli(["clean", workspace])
    assert result.exit_code == 0
    count = 0
    for root, _, files in os.walk(workspace, topdown=False):
        for name in files:
            if not name.endswith(("___metadata.xml", "___metadata.csv",
                                  "testfile1.wav")):
                count = count + 1
    assert count == 0
