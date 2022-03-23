"""Test Music Archive adaptor.
"""
from dpres_sip_compiler.adaptors.musicarchive import (
    SipMetadataMusicArchive,
    PremisObjectMusicArchive,
    PremisEventMusicArchive,
    PremisAgentMusicArchive,
    PremisLinkingMusicArchive
)
from dpres_sip_compiler.config import Config


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
    assert set(desc_files) == set([
        "tests/data/musicarchive/source1/test1___metadata.xml",
        "tests/data/musicarchive/source1/test2___metadata.xml"])


def test_find_path():
    """Check that path is found.
    """
    source_dict = {
        "objekti-uuid": "object-id-123",
        "objekti-nimi": "testfile1.wav",
        "tiiviste-tyyppi": "MD5",
        "tiiviste": "abc"
    }
    obj = PremisObjectMusicArchive(source_dict)
    obj.find_path("tests/data/musicarchive/source1")
    assert obj.filepath == "audio/testfile1.wav"


def test_object_properties():
    """Test that object properties result values from given dict.
    """
    source_dict = {
        "objekti-uuid": "object-id-123",
        "objekti-nimi": "filename",
        "tiiviste-tyyppi": "MD5",
        "tiiviste": "abc"
    }
    obj = PremisObjectMusicArchive(source_dict)
    assert obj.identifier == "object-id-123"
    assert obj.object_identifier_type == "UUID"
    assert obj.object_identifier_value == "object-id-123"
    assert obj.original_name == "filename"
    assert obj.message_digest_algorithm == "MD5"
    assert obj.message_digest == "abc"


def test_event_properties():
    """Test that event properties result values from given dict.
    """
    source_dict = {
        "event-id": "event-id-123",
        "event": "message digest calculation",
        "event-aika": "2022-02-01 14:00:00",
        "event-tulos": "success",
        "tiiviste": "abc",
        "tiiviste-tyyppi": "MD5",
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
    assert event.event_datetime == "2022-02-01T14:00:00"
    assert event.event_outcome == "success"
    assert event.event_detail == "Checksum calculation for digital objects."
    assert event.event_outcome_detail == \
        "Checksum calculated with algorithm MD5 resulted the following " \
        "checksums:\nfilename: abc"


def test_add_detail_info():
    """Test that detailed info is added without duplicates.
    """
    source_dict = {
        "event-id": "event-id-123",
        "event": "message digest calculation",
        "event-aika": "2022-02-01 14:00:00",
        "event-tulos": "success",
        "tiiviste": "abc",
        "tiiviste-tyyppi": "MD5",
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
             "following checksums:\nfilename1: abc\nfilename2: def"
    assert event.event_outcome_detail == detail
    assert len(event._detail_info) == 2


def test_agent_properties():
    """Test that agent properties result values from given dict.
    """
    source_dict = {
        "agent-id": "agent-id-123",
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
