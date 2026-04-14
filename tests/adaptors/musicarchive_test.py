"""Test Music Archive adaptor.
"""
import os
import shutil

import pytest
from dpres_sip_compiler import constants
from dpres_sip_compiler.adaptors.musicarchive import (
    PremisAgentMusicArchive,
    PremisEventMusicArchive,
    PremisLinkingMusicArchive,
    PremisObjectMusicArchive,
    PremisRepresentationMusicArchive,
    SipMetadataMusicArchive,
    handle_html_files,
)
from dpres_sip_compiler.compiler import compile_sip
from dpres_sip_compiler.config import Config
from lxml import etree


def test_populate():
    """Test that CSV is populated.
    """
    sip_meta = SipMetadataMusicArchive()
    config = Config(conf_file="tests/data/musicarchive/config.conf")
    sip_meta.populate("tests/data/musicarchive/source1", config)
    assert len(sip_meta.premis_objects) == 4
    assert len(sip_meta.premis_events) == 7
    assert len(sip_meta.premis_agents) == 3
    assert len(sip_meta.premis_linkings) == 7


def test_populate_deprecatedsum():
    """
    Test that PREMIS object is not created for old checksum, but the event is.
    """
    sip_meta = SipMetadataMusicArchive()
    config = Config(conf_file="tests/data/musicarchive/config.conf")
    sip_meta.populate("tests/data/musicarchive/source2", config)

    assert sip_meta.premis_objects[
        '882d63db-c9b6-4f44-83ba-901b300821cc'].digest_valid
    assert "deprecatedsum" in sip_meta.premis_events['3'].event_outcome_detail
    assert "abc123" in sip_meta.premis_events['4'].event_outcome_detail

    assert len(sip_meta.premis_objects) == 1
    assert len(sip_meta.premis_events) == 3
    assert len(sip_meta.premis_agents) == 1
    assert len(sip_meta.premis_linkings) == 3


def test_descriptive_files():
    """Check that descriptive metadata files are found.
    """
    sip_meta = SipMetadataMusicArchive()
    config = Config(conf_file="tests/data/musicarchive/config.conf")
    desc_files = []
    for (dataformat, desc) in sip_meta.descriptive_metadata_sources(
            ["tests/data/musicarchive/source1"], config):
        desc_files.append(desc)
        assert dataformat == 'file'
    assert set(desc_files) == {
        "tests/data/musicarchive/source1/test1___metadata.xml",
        "tests/data/musicarchive/source1/test2___metadata.xml"}


def test_find_path():
    """Check that path is found.
    """
    source_dict = {
        "objekti-uuid": "object-id-123",
        "objekti-nimi": "testfile1.wav",
        "tiiviste-tyyppi": "MD5",
        "tiiviste": "abc",
        "objekti-id": "alt-123",
        "poo-sip-obj-x-rooli-selite": "null",
        "event": "null"
    }
    obj = PremisObjectMusicArchive(source_dict)
    obj.find_path("tests/data/musicarchive/source1")
    assert obj.filepath == "audio/testfile1.wav"


def test_alt_identifier(tmpdir):
    """
    Test appending an alternative PREMIS object identifier to METS
    """
    xml_original = \
        """
        <mets:mets xmlns:mets="http://www.loc.gov/METS/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns:premis="info:lc/xmlns/premis-v2">
        <mets:amdSec><mets:techMD ID="tech014" CREATED="2015-04-29">
        <mets:mdWrap><mets:xmlData>
        <premis:object xsi:type="premis:file">
          <premis:objectIdentifier>
            <premis:objectIdentifierType>UUID</premis:objectIdentifierType>
            <premis:objectIdentifierValue>882d63db-c9b6-4f44-83ba-901b300821cc
            </premis:objectIdentifierValue>
          </premis:objectIdentifier>
        <premis:objectCharacteristics /></premis:object>
        </mets:xmlData></mets:mdWrap></mets:techMD></mets:amdSec>
        </mets:mets>"""
    mets_file = os.path.join(str(tmpdir), "mets.xml")
    with open(mets_file, 'w', encoding='utf-8') as outfile:
        outfile.write(xml_original)
    sip_meta = SipMetadataMusicArchive()
    config = Config(conf_file="tests/data/musicarchive/config.conf")
    sip_meta.populate("tests/data/musicarchive/source2", config)

    mets_xml = etree.parse(mets_file).getroot()
    premis_ids = mets_xml.xpath(
        ".//premis:objectIdentifier",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})

    assert len(premis_ids) == 1
    assert premis_ids[0].xpath(
        "./premis:objectIdentifierType",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'}
        )[0].text.strip() == "UUID"
    assert premis_ids[0].xpath(
        "./premis:objectIdentifierValue",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'}
        )[0].text.strip() == "882d63db-c9b6-4f44-83ba-901b300821cc"


def test_handle_html_files(sample_mets, path_to_files):
    """
    Test that invalid HTML files are marked as TXT in METS file and format
    version is removed.
    Test that for valid HTML files the METS file content does not change.
    """
    mets_xml = handle_html_files(sample_mets, path_to_files)
    format_elem = mets_xml.xpath(
        ".//premis:format",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})
    # invalid html
    assert (format_elem[0].xpath(
        "./premis:formatDesignation/premis:formatName",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})[0].text.strip()
            == "text/plain; alt-format=text/html")
    assert len(format_elem[0].xpath(
        "./premis:formatDesignation/premis:formatVersion",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})) == 0
    # valid html
    assert (format_elem[1].xpath(
        "./premis:formatDesignation/premis:formatName",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})[0].text.strip()
            == "text/html; charset=UTF-8")
    assert len(format_elem[1].xpath(
        "./premis:formatDesignation/premis:formatVersion",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})) == 1


def test_object_properties():
    """Test that object properties result values from given dict.
    """
    source_dict = {
        "objekti-uuid": "object-id-123",
        "objekti-nimi": "filename",
        "tiiviste-tyyppi": "MD5",
        "tiiviste": "abc",
        "objekti-id": "alt-123",
        "bit_level": False,
    }
    obj = PremisObjectMusicArchive(source_dict)
    assert obj.identifier == "object-id-123"
    assert obj.object_identifier_type == "UUID"
    assert obj.object_identifier_value == "object-id-123"
    assert obj.original_name == "filename"
    assert obj.message_digest_algorithm == "MD5"
    assert obj.message_digest == "abc"
    assert obj.alt_identifier_type == "local"
    assert obj.alt_identifier_value == "alt-123"
    assert obj.bit_level is False


def test_event_properties():
    """Test that event properties result values from given dict.
    """
    source_dict = {
        "event-id": "event-id-123",
        "event": "message digest calculation",
        "event-aika-alku": "2022-02-01 14:00:00",
        "event-aika-loppu": "2022-02-01 14:00:15",
        "event-selite": "null",
        "event-tulos": "success",
        "tiiviste": "abc",
        "tiiviste-tyyppi": "MD5",
        "tiiviste-aika": "2022-02-01 14:00:05",
        "pon-korvattu-nimi": None,
        "objekti-nimi": "filename",
        "sip-tunniste": "sip-123",
    }
    event = PremisEventMusicArchive(source_dict)
    event.add_detail_info(source_dict)
    assert event.identifier == "event-id-123"
    assert event.event_identifier_type == "local"
    assert event.event_identifier_value == "event-id-123"
    assert event.event_type == "message digest calculation"
    assert event.event_datetime == "2022-02-01T14:00:00/2022-02-01T14:00:15"
    assert event.event_outcome == "success"
    assert event.event_detail == "Checksum calculation for digital objects."
    assert event.event_outcome_detail == \
        "Checksum calculated with algorithm MD5 resulted the following " \
        "checksums:\nfilename: abc (timestamp: 2022-02-01T14:00:05)"


@pytest.mark.parametrize("end_timestamp",
                         ["NULL",
                          "2022-02-01 14:00:00"])
def test_event_noend(end_timestamp):
    """Test a case where event timestamp in CSV is not periodic.
    """
    source_dict = {
        "event-id": "event-id-123",
        "event": "test event",
        "event-aika-alku": "2022-02-01 14:00:00",
        "event-aika-loppu": end_timestamp,
        "event-selite": "null",
        "event-tulos": "success",
        "tiiviste": None,
        "tiiviste-tyyppi": None,
        "tiiviste-aika": None,
        "pon-korvattu-nimi": None,
        "objekti-nimi": "filename",
        "sip-tunniste": "sip-123",
    }
    event = PremisEventMusicArchive(source_dict)
    event.add_detail_info(source_dict)
    assert event.event_datetime == "2022-02-01T14:00:00"


def test_add_detail_info():
    """Test that detailed info is added without duplicates.
    """
    source_dict = {
        "event-id": "event-id-123",
        "event": "message digest calculation",
        "event-aika-alku": "2022-02-01 14:00:00",
        "event-aika-loppu": "2022-02-01 14:00:15",
        "event-selite": "null",
        "event-tulos": "success",
        "tiiviste": "abc",
        "tiiviste-tyyppi": "MD5",
        "tiiviste-aika": "2022-02-01 14:00:05",
        "pon-korvattu-nimi": None,
        "objekti-nimi": "filename1",
        "sip-tunniste": "sip-123",
    }
    event = PremisEventMusicArchive(source_dict)
    event.add_detail_info(source_dict)
    copy_dict = source_dict.copy()
    copy_dict["tiiviste"] = "def"
    copy_dict["objekti-nimi"] = "filename2"
    event.add_detail_info(copy_dict)
    event.add_detail_info(source_dict)
    detail = "Checksum calculated with algorithm MD5 resulted the " \
             "following checksums:\nfilename1: abc (timestamp: " \
             "2022-02-01T14:00:05)\nfilename2: def (timestamp: " \
             "2022-02-01T14:00:05)"
    assert event.event_outcome_detail == detail
    assert len(event._detail_info) == 2  # pylint: disable=protected-access

    source_dict["event-selite"] = "Given detail."
    event = PremisEventMusicArchive(source_dict)
    event.add_detail_info(source_dict)
    detail = "Checksum calculated with algorithm MD5 resulted the " \
             "following checksums:\nfilename1: abc (timestamp: " \
             "2022-02-01T14:00:05)"
    assert event.event_outcome_detail == "Given detail.\n\n%s" % detail


def test_agent_properties():
    """Test that agent properties result values from given dict.
    """
    source_dict = {
        "agent-id": "id-123",
        "agent-nimi": "Test agent",
        "agent-tyyppi": "tester",
    }
    agent = PremisAgentMusicArchive(source_dict)
    assert agent.identifier == "agent-id-123"
    assert agent.agent_identifier_type == "local"
    assert agent.agent_identifier_value == "agent-id-123"
    assert agent.agent_name == "Test agent"
    assert agent.agent_type == "tester"


def test_skip_object():
    """Test that object linking is skipped if event type is related to
    information package creation.
    """
    source_row = {
        "event-id": "event-id-123",
        "event": "information package creation",
        "poo-sip-obj-x-rooli-selite": "null",
        "poo-vastinpari-obj-uuid": "null",
        "poo-vastinpari-obj-id": "null",
        "poo-vastinpari-obj-nimi": "null",
        "poo-vastinpari-obj-status": "null"
    }
    linking = PremisLinkingMusicArchive(source_row)
    linking.add_object_link(1, "null")
    assert not linking.object_links


def test_skip_hidden(tmpdir, pick_files_tar):
    """
    Test that we do not pick hidden files in SIP compilation
    in Music Archive adaptor.
    """

    source_path = os.path.join(str(tmpdir), "source1")
    shutil.copytree("tests/data/musicarchive/source1", source_path)

    hidden = os.path.join(source_path, ".hidden_file")
    open(hidden, "w").close()
    assert os.path.isfile(hidden)

    tar_file = os.path.join(str(tmpdir), "sip.tar")
    compile_sip(
        source_path=source_path,
        tar_file=tar_file,
        conf_file="tests/data/musicarchive/config.conf"
    )
    assert os.path.isfile(tar_file)
    tar_list = pick_files_tar(tar_file)
    assert ".hidden_file" not in " ".join(tar_list)


def test_representation_properties():
    """Test that representation properties result values from given dict.
    """
    source_dict = {
        "poo-vastinpari-obj-uuid": "test_uuid_123",
        "poo-vastinpari-obj-nimi": "missing_original_file.txt",
        "poo-vastinpari-obj-id": "test_id_123",
        "poo-vastinpari-obj-status": "xxx",
        "objekti-nimi": "test_outcome_file123.txt"
    }
    representation = PremisRepresentationMusicArchive(source_dict)
    assert representation.object_identifier_type == "UUID"
    assert representation.object_identifier_value == "test_uuid_123"
    assert representation.original_name == "missing_original_file.txt"
    assert representation.alt_identifier_type == "local"
    assert representation.alt_identifier_value == "test_id_123"
    assert representation.object_status == "xxx"
    assert representation.outcome_filename == "test_outcome_file123.txt"


def test_scrape_dv_file():
    """Test the scrape_objects method with DV conversion file case.

    The DV file is the source object of a conversion event, this is
    recorded by musicarchive in the CSV metadata. DV files
    should additionally be forensically analysed by the musicarchive
    adaptor, by running the dvanalyzer command during packaging and
    documenting the results.

    The test tests that both types of events are recorded in the SIP
    METS document.
    """
    sip_meta = SipMetadataMusicArchive()
    config = Config(conf_file="tests/data/musicarchive/config.conf")
    sip_meta.populate(
        "tests/data/musicarchive/conversion_dv_test_case", config)
    sip_meta.scrape_objects(
        "tests/data/musicarchive/conversion_dv_test_case", True)
    events = list(sip_meta.events)
    links = list(sip_meta.linkings)

    # Check that forensic feature analysis event is created
    assert any(
        event.event_type == constants.EVENT_FORENSIC
        for event in events
    )
    assert any(
        (b'<event type="error" event_id="1" '
         b'event_type="video error concealment">59.53% (893 F errors)</event>')
        in etree.tostring(event.event_outcome_detail_extension)
        for event in list(sip_meta.events)
        if event.event_outcome_detail_extension is not None
    )

    # Check that the conversion event is recorded in the metadata
    assert any(
        event.event_type == constants.EVENT_CONVERSION
        for event in events
    )

    # Check that the DV file is target and the dvanalyzer tool is the
    # executing program
    assert any(
        (
            any(
                obj["linking_object"] == "882d63db-c9b6-4f44-83ba-901b300821cc"
                and obj["object_role"] == "target"
                for obj in link.object_links
            )
            and any(
                agt["linking_agent"] == "dvanalyzer"
                and agt["agent_role"] == "executing program"
                for agt in link.agent_links
            )
        )
        for link in links
    )

    # Check that the DV file is source and the MP4 file is óutcome
    assert any(
        (
            any(
                obj["linking_object"] == "882d63db-c9b6-4f44-83ba-901b300821cc"
                and obj["object_role"] == "source"
                for obj in link.object_links
            )
            and any(
                obj["linking_object"] == "982d63db-c9b6-4f44-83ba-901b300821cc"
                and obj["object_role"] == "outcome"
                for obj in link.object_links
            )
        )
        for link in links
    )
