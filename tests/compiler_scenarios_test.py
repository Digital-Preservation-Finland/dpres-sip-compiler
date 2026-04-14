"""Test Compiler scenarios - migration and normalization use cases.
"""
from __future__ import annotations

import os
from typing import Any, Callable
import pytest
from lxml import etree
from dpres_sip_compiler.compiler import compile_sip
from dpres_sip_compiler.constants import (
    FILE_USE_IGNORE_VALIDATION,
    FILE_USE_FORENSIC_ANALYSIS,
    FILE_USE_NO_VALIDATION
)

_NAMESPACES = {
    "mets": "http://www.loc.gov/METS/",
    "premis": "info:lc/xmlns/premis-v2",
    "xlink": "http://www.w3.org/1999/xlink",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def _assert_html_content(mets_filepath: str) -> None:
    """Shorthand function to validate the mets content of accepted html
    test package for musicarchive.

    :param mets_filepath: Path to the mets.xml file.
    """
    xml_tree = etree.parse(mets_filepath)
    format_name_element = xml_tree.xpath(
        (
            "./mets:amdSec/mets:techMD/mets:mdWrap/mets:xmlData/premis:object"
            '/premis:originalName[text()="invalid_html.html"]'
            "/preceding-sibling::premis:objectCharacteristics"
            "/premis:format/premis:formatDesignation/premis:formatName"
        ),
        namespaces=_NAMESPACES,
    )[0]
    assert (
        format_name_element.text
        == "text/plain; alt-format=text/html; charset=UTF-8"
    )


def _assert_migration_content(mets_filepath: str) -> None:
    """Shorthand function to validate the mets content of migration test
    package for musicarchive.

    :param mets_filepath: Path to the mets.xml file.
    """
    xml_tree = etree.parse(mets_filepath)

    # Files that should not have "USE" attribute, because they are
    # supported and have no issues during file-scraping
    no_use_files = [
        # Migration outcome
        "test_file_migrated_01.txt",
        # Migration outcome
        "test_file_migrated_02.txt",
        # Normalized outcome
        "test_file_normalized_01.txt",
        # Normalized outcome
        "test_file_normalized_02.txt",
    ]
    for no_use_file in no_use_files:
        no_use_file_elem = xml_tree.xpath(
            (
                "./mets:fileSec/mets:fileGrp/mets:file["
                ".//mets:FLocat["
                f'@xlink:href="file:///files/{no_use_file}"]]'
            ),
            namespaces=_NAMESPACES,
        )[0]
        assert no_use_file_elem.attrib.get("USE") is None

    # Files that are not supported used as source for migration and
    # normalization should use "USE" with
    # "fi-dpres-no-file-format-validation"
    bit_level_files = [
        # Migration source
        "test_file_original_01.atlproj",
        # Normalization source
        "test_file_original_02.atlproj",
    ]
    for bit_level_file in bit_level_files:
        bit_level_file_elem = xml_tree.xpath(
            (
                "./mets:fileSec/mets:fileGrp/mets:file["
                ".//mets:FLocat["
                f'@xlink:href="file:///files/{bit_level_file}"]]'
            ),
            namespaces=_NAMESPACES,
        )[0]
        assert (
            bit_level_file_elem.attrib.get("USE")
            == FILE_USE_NO_VALIDATION
        )

    # Files that are supported, but outright broken, thus used as
    # migration or normalization source and use "USE" with
    # "fi-dpres-ignore-validation-errors"
    broken_source_file_elem = xml_tree.xpath(
        (
            "./mets:fileSec/mets:fileGrp/mets:file["
            ".//mets:FLocat["
            '@xlink:href="file:///files/test_file_original_04.jpg"]]'
        ),
        namespaces=_NAMESPACES,
    )[0]
    assert (
        broken_source_file_elem.attrib.get("USE")
        == FILE_USE_IGNORE_VALIDATION
    )


def _assert_conversion_content(mets_filepath: str) -> None:
    """Shorthand function to validate the mets content of conversion
    metadata for musicarchive.

    :param mets_filepath: Path to the mets.xml file.
    """
    xml_tree = etree.parse(mets_filepath)

    # Outcome file should not have a "USE" attribute, because it is
    # supported and have no issues during file-scraping
    no_use_target_file_elem = xml_tree.xpath(
        (
            "./mets:fileSec/mets:fileGrp/mets:file["
            ".//mets:FLocat["
            '@xlink:href="file:///video/h265_derivative_version.mp4"]]'
        ),
        namespaces=_NAMESPACES,
    )[0]
    assert no_use_target_file_elem.attrib.get("USE") is None

    # Musicarchive's converted source should always ignore certain
    # validation messages with "USE" and
    # "fi-dpres-preserve-forensically-analysed-object"
    source_used_for_converted_file_elem = xml_tree.xpath(
        (
            "./mets:fileSec/mets:fileGrp/mets:file["
            ".//mets:FLocat["
            '@xlink:href="file:///video/'
            'dv_with_concealing_bitstream_errors.dv"]]'
        ),
        namespaces=_NAMESPACES,
    )[0]
    assert (
        source_used_for_converted_file_elem.attrib.get("USE")
        == FILE_USE_FORENSIC_ANALYSIS
    )


def _assert_postalmuseum_mets_content(
        mets_filepath: str, content_id: str, sip_id: str) -> None:
    """Shorthand function to validate the mets content of accepted
    test package for postal museum.

    The METS should contain two dmdSec sections containing LIDO
    metadata.

    :param mets_filepath: Path to the mets.xml file.
    """
    xml_tree = etree.parse(mets_filepath)
    root = xml_tree.getroot()
    fi_ns = 'http://digitalpreservation.fi/schemas/mets/fi-extensions'
    assert root.get(f'{{{fi_ns}}}CONTENTID') == content_id
    assert root.get('OBJID') == sip_id
    mdwrap_elements = xml_tree.xpath(
        (
            './mets:dmdSec/mets:mdWrap[@MDTYPE="LIDO"]'
        ),
        namespaces=_NAMESPACES,
    )
    assert len(mdwrap_elements) == 2
    for mdwrap_element in mdwrap_elements:
        assert mdwrap_element.get('MDTYPEVERSION') == '1.1'
        xmldata_elem = mdwrap_element.xpath(
            (
                './mets:xmlData'
            ),
            namespaces=_NAMESPACES
        )[0]
        assert len(xmldata_elem) == 1
        for child_elem in xmldata_elem:
            assert child_elem.tag == '{http://www.lido-schema.org}lidoWrap'


def test_compile_sip(tmpdir: Any,
                     pick_files_tar: Callable[[str], list[str]]) -> None:
    """Test sip compilation."""
    tar_file = os.path.join(str(tmpdir), "test_sip.tar")
    compile_sip(
        source_path="tests/data/generic/files",
        descriptive_metadata_paths=[
            "tests/data/generic/desc_dc_metadata.xml"
        ],
        tar_file=tar_file,
        conf_file="tests/data/generic/generic.conf",
        validation=False
    )
    assert os.path.isfile(tar_file)
    tar_list = pick_files_tar(tar_file)
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list
    assert "test_file_01.txt" in tar_list
    assert "test_file_02.txt" in tar_list


@pytest.mark.parametrize(
    "package_source",
    ["accepted_html_files",
     "source1",
     "migration_test_files",
     "conversion_dv_test_case"],
)
def test_musicarchive_compile(
        tmp_path: Any,
        pick_files_tar: Callable[[str, Any, list[str]], list[str]],
        package_source: str) -> None:
    """Test sip compilation for music archives."""
    musicarchive_path = "tests/data/musicarchive"
    conf_path = f"{musicarchive_path}/config.conf"
    tar_file = tmp_path / "test_sip.tar"
    tmp_tar_dir = tmp_path / "extracted_tar_contents"
    compile_sip(
        source_path=f"{musicarchive_path}/{package_source}",
        tar_file=str(tar_file),
        conf_file=conf_path,
        descriptive_metadata_paths=None,
        validation=False
    )
    assert os.path.isfile(tar_file)
    tar_list = pick_files_tar(
        tar_file, target=tmp_tar_dir, extract_list=["mets.xml"]
    )
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list
    if package_source == "accepted_html_files":
        _assert_html_content(mets_filepath=str(tmp_tar_dir / "mets.xml"))
    elif package_source == "migration_test_files":
        _assert_migration_content(mets_filepath=str(tmp_tar_dir / "mets.xml"))
    elif package_source == "conversion_dv_test_case":
        _assert_conversion_content(mets_filepath=str(tmp_tar_dir / "mets.xml"))


def test_postalmuseum_compile(
        tmp_path: Any,
        pick_files_tar: Callable[[str, Any, list[str]], list[str]]) -> None:
    """Test sip compilation for postal museum."""
    postalmuseum_path = "tests/data/postalmuseum"
    conf_path = f"{postalmuseum_path}/postalmuseum.conf"
    tar_file = tmp_path / "test_sip.tar"
    tmp_tar_dir = tmp_path / "extracted_tar_contents"
    content_id = "Test1"
    sip_id = "Test-001"
    compile_sip(
        source_path=f"{postalmuseum_path}/files",
        tar_file=str(tar_file),
        conf_file=conf_path,
        descriptive_metadata_paths=[
            f"{postalmuseum_path}/lido_example_multiple_lidowraps.lido"],
        content_id=content_id,
        sip_id=sip_id,
        validation=False
    )
    assert os.path.isfile(tar_file)
    tar_list = pick_files_tar(
        tar_file, target=tmp_tar_dir, extract_list=["mets.xml"]
    )
    assert "mets.xml" in tar_list
    assert "signature.sig" in tar_list
    assert "test_file_01.txt" in tar_list
    assert "test_file_02.txt" in tar_list
    _assert_postalmuseum_mets_content(
        mets_filepath=str(tmp_tar_dir / "mets.xml"),
        content_id=content_id,
        sip_id=sip_id)
