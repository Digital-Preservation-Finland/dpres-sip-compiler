"""
"""
from dpres_sip_compiler.adaptors.musicarchive import (
    PremisObjectMusicArchive,
    PremisEventMusicArchive,
    PremisAgentMusicArchive,
    PremisLinkingMusicArchive
)


def test_object_properties():
    """
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
    """
    """
    source_dict = {
        "event-id": "event-id-123",
        "event": "message digest calculation",
        "event-aika": "2022-02-01T14:00:00",
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


def test_agent_properties():
    """
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
    """
    """
    source_row = {
        "event-id": "event-id-123",
        "event": "information package creation"
    }
    linking = PremisLinkingMusicArchive(source_row)
    linking.add_object_link(1)
    assert linking.object_links == []
