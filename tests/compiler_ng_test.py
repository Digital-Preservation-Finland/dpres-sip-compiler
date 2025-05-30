"""Test SIP compilation with compiler-ng.
"""
import os
import pytest
from dpres_sip_compiler.compiler_ng import ng_compile_sip


def test_ng_compile_sip(tmpdir, pick_files_tar):
    """Test sip compilation."""
    tar_file = os.path.join(str(tmpdir), "test_sip.tar")
    ng_compile_sip(
        "tests/data/compiler_ng/files",
        descriptive_metadata_paths=[
            "tests/data/compiler_ng/desc_dc_metadata.xml"
        ],
        tar_file=tar_file,
        conf_file="tests/data/compiler_ng/generic.conf")
    assert os.path.isfile(tar_file)
    tar_list = pick_files_tar(tar_file)
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list
    assert "test_file_01.txt" in tar_list
    assert "test_file_02.txt" in tar_list


@pytest.mark.parametrize(
    "package_source",
    ["accepted_html_files", "source1", "migration_test_files"],
)
def test_musicarchive_compile_ng(tmp_path, pick_files_tar, package_source):
    """Test sip compilation for music archives."""
    musicarchive_path = "tests/data/musicarchive"
    conf_path = f"{musicarchive_path}/config.conf"
    tar_file = tmp_path / "test_sip.tar"
    ng_compile_sip(
        source_path=f"{musicarchive_path}/{package_source}",
        tar_file=str(tar_file),
        conf_file=conf_path,
    )
    assert os.path.isfile(tar_file)
    tar_list = pick_files_tar(tar_file)
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list
