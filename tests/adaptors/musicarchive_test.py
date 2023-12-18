"""Test Music Archive adaptor.
"""
import os
import shutil
import pytest
import lxml
from dpres_sip_compiler.adaptors.musicarchive import (
    SipMetadataMusicArchive,
    PremisObjectMusicArchive,
    PremisEventMusicArchive,
    PremisAgentMusicArchive,
    PremisLinkingMusicArchive
)
from dpres_sip_compiler.config import Config
from dpres_sip_compiler.compiler import compile_sip



def test_populate():
    """Test that CSV is populated.
    """
    sip_meta = SipMetadataMusicArchive()
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
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
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
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
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
    desc_files = []
    for desc in sip_meta.descriptive_files(
            "tests/data/musicarchive/source1", config):
        desc_files.append(desc)
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
        "objekti-id": "alt-123"
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
        <mets:amdSec><mets:techMD ID="tech014" CREATED="2015-04-29"><mets:mdWrap><mets:xmlData>
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
    with open(mets_file, 'w') as outfile:
        outfile.write(xml_original)
    sip_meta = SipMetadataMusicArchive()
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
    sip_meta.populate("tests/data/musicarchive/source2", config)
    sip_meta.post_tasks(str(tmpdir))
    mets_xml = lxml.etree.parse(mets_file).getroot()
    premis_ids = mets_xml.xpath(
        ".//premis:objectIdentifier",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})
    assert premis_ids[0].xpath(
        "./premis:objectIdentifierType",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'}
        )[0].text.strip() == "UUID"
    assert premis_ids[0].xpath(
        "./premis:objectIdentifierValue",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'}
        )[0].text.strip() == "882d63db-c9b6-4f44-83ba-901b300821cc"
    assert premis_ids[1].xpath(
        "./premis:objectIdentifierType",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'}
        )[0].text.strip() == "local"
    assert premis_ids[1].xpath(
        "./premis:objectIdentifierValue",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'}
        )[0].text.strip() == "123"
    assert len(mets_xml.xpath(
        ".//premis:objectIdentifier",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})) == 2

    # Test that alt ID can not be added twice
    sip_meta.post_tasks(str(tmpdir))
    mets_xml = lxml.etree.parse(mets_file).getroot()
    assert len(mets_xml.xpath(
        ".//premis:objectIdentifier",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})) == 2

def test_handle_html_files(tmpdir):
    """
    Test appending an alternative PREMIS object identifier to METS
    """
    xml_original = \
        """
        <mets:mets xmlns:mets="http://www.loc.gov/METS/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns:premis="info:lc/xmlns/premis-v2"
                   xmlns:xlink="http://www.w3.org/1999/xlink">
        <mets:amdSec><mets:techMD ID="tech014" CREATED="2015-04-29"><mets:mdWrap><mets:xmlData>
        <premis:object xsi:type="premis:file">
          <premis:objectIdentifier>
            <premis:objectIdentifierType>UUID</premis:objectIdentifierType>
            <premis:objectIdentifierValue>882d63db-c9b6-4f44-83ba-901b300821cc
            </premis:objectIdentifierValue>
          </premis:objectIdentifier>
        <premis:objectCharacteristics>
            <premis:format>
                <premis:formatDesignation>
                    <premis:formatName>text/html</premis:formatName>
                    <premis:formatVersion>1a</premis:formatVersion>
                </premis:formatDesignation>
            </premis:format>
        </premis:objectCharacteristics>
        </premis:object>
        </mets:xmlData></mets:mdWrap></mets:techMD></mets:amdSec>
        <mets:fileSec>
		<mets:fileGrp>
			<mets:file ID="file014" ADMID="tech014 event-pdf-pdfa agent-csc agent-gs">
				<mets:FLocat LOCTYPE="URL" xlink:type="simple" xlink:href="file://testi.html"/>
			</mets:file>
		</mets:fileGrp>
        		<mets:fileGrp>
			<mets:file ID="file015" ADMID="tech015 event-pdf-pdfa agent-csc agent-gs">
				<mets:FLocat LOCTYPE="URL" xlink:type="simple" xlink:href="file://data/invalid_html.html"/>
			</mets:file>
		</mets:fileGrp>

    	</mets:fileSec>

        </mets:mets>"""
    mets_file = os.path.join(str(tmpdir), "mets.xml")
    with open(mets_file, 'wt') as outfile:
        outfile.write(xml_original)
    sip_meta = SipMetadataMusicArchive()
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
    sip_meta.populate("tests/data/musicarchive/source2", config)
    sip_meta.post_tasks(str(tmpdir), config)
    mets_xml = lxml.etree.parse(mets_file).getroot()
    html_file = mets_xml.xpath(
        ".//premis:objectCharacteristics",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})
    assert html_file[0].xpath(
        "./premis:format/premis:formatDesignation/premis:formatName",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})[0].text.strip() == "text/plain; alt-format=text/html"
    assert len(html_file[0].xpath(
        "./premis:format/premis:formatDesignation/premis:formatVersion",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})[0]) == 0



def test_object_properties():
    """Test that object properties result values from given dict.
    """
    source_dict = {
        "objekti-uuid": "object-id-123",
        "objekti-nimi": "filename",
        "tiiviste-tyyppi": "MD5",
        "tiiviste": "abc",
        "objekti-id": "alt-123"
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
        "sip-tunniste": "sip-123"
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
        "sip-tunniste": "sip-123"
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
        "sip-tunniste": "sip-123"
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
        "event": "information package creation"
    }
    linking = PremisLinkingMusicArchive(source_row)
    linking.add_object_link(1)
    assert linking.object_links == []


def test_skip_hidden(tmpdir, pick_files_tar):
    """
    Test that we do not pick hidden files in SIP compilation
    in Music Archive adaptor.
    """
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")

    source_path = os.path.join(str(tmpdir), "source1")
    shutil.copytree("tests/data/musicarchive/source1", source_path)

    hidden = os.path.join(source_path, ".hidden_file")
    open(hidden, "w").close()
    assert os.path.isfile(hidden)

    tar_file = os.path.join(str(tmpdir), "sip.tar")
    compile_sip(source_path, tar_file, str(tmpdir),
                "tests/data/musicarchive/config.conf")

    assert os.path.isfile(tar_file)
    tar_list = pick_files_tar(tar_file, None, None)
    assert not "./.hidden_file" in tar_list
    assert "./mets.xml" in tar_list
    assert "./signature.sig" in tar_list
