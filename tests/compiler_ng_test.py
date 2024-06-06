"""Test SIP compilation with compiler-ng.
"""
import os
import pytest
from dpres_sip_compiler.compiler_ng import ng_compile_sip


def test_ng_compile_sip(tmpdir, pick_files_tar):
    """Test sip compilation."""
    tar_file = os.path.join(str(tmpdir), "test_sip.tar")
    ng_compile_sip("tests/data/compiler_ng/files",
                   "tests/data/compiler_ng/desc_dc_metadata.xml",
                   tar_file=tar_file,
                   conf_file="tests/data/compiler_ng/generic.conf")
    assert os.path.isfile(tar_file)
    tar_list = pick_files_tar(tar_file)
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list
    assert "test_file_01.txt" in tar_list
    assert "test_file_02.txt" in tar_list
