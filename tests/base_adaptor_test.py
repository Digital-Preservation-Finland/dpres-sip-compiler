"""Test Base adaptor.
"""
from dpres_sip_compiler.base_adaptor import (
    SipMetadata, PremisObject, PremisEvent, PremisAgent, PremisLinking,
    build_sip_metadata
)
from dpres_sip_compiler.adaptor_list import ADAPTOR_DICT
from dpres_sip_compiler.config import Config


def test_build_sip_meta():
    """Test that the class is selected based on configuration.
    """
    config = Config()
    config.configure("tests/data/musicarchive/config.conf")
    sip_meta = build_sip_metadata(
        ADAPTOR_DICT, "tests/data/musicarchive/source1", config)
    assert sip_meta.__class__.__name__ == "SipMetadataMusicArchive"


class PremisObjectTest(PremisObject):
    """Test class for objects.
    """
    def __init__(self, identifier):
        """Set given identifier.
        """
        super(PremisObjectTest, self).__init__()
        self._identifier = identifier

    @property
    def identifier(self):
        """Return given identifier.
        """
        return self._identifier


class PremisEventTest(PremisEvent):
    """Test class for events.
    """
    def __init__(self, identifier):
        """Set given identifier.
        """
        super(PremisEventTest, self).__init__()
        self._identifier = identifier

    @property
    def identifier(self):
        """Return given identifier.
        """
        return self._identifier


class PremisAgentTest(PremisAgent):
    """Test class for agents.
    """
    def __init__(self, identifier):
        """Set given identifier.
        """
        super(PremisAgentTest, self).__init__()
        self._identifier = identifier

    @property
    def identifier(self):
        """Return given identifier.
        """
        return self._identifier


class PremisLinkingTest(PremisLinking):
    """Test class for linkings.
    """
    def __init__(self, identifier):
        """Set given identifier as identifier.
        """
        super(PremisLinkingTest, self).__init__()
        self.identifier = identifier


def test_objects():
    """Tests that objects can be added without duplicates.
    """
    test_object1 = PremisObjectTest(1)
    test_object2 = PremisObjectTest(2)
    sip_meta = SipMetadata()
    sip_meta.add_object(test_object1)
    sip_meta.add_object(test_object2)
    sip_meta.add_object(test_object1)  # Duplicate, not added
    assert len(sip_meta.premis_objects) == 2
    assert sip_meta.premis_objects[1]
    assert sip_meta.premis_objects[2]

    count = 0
    for obj in sip_meta.objects:
        count = count + 1
    assert count == 2


def test_events():
    """Test that events can be added without duplicates.
    """
    test_event1 = PremisEventTest(1)
    test_event2 = PremisEventTest(2)
    sip_meta = SipMetadata()
    sip_meta.add_event(test_event1)
    sip_meta.add_event(test_event2)
    sip_meta.add_event(test_event1)  # Duplicate, not added
    assert len(sip_meta.premis_events) == 2
    assert sip_meta.premis_events[1]
    assert sip_meta.premis_events[2]

    count = 0
    for obj in sip_meta.events:
        count = count + 1
    assert count == 2


def test_agents():
    """Test that agents can be added without duplicates.
    """
    test_agent1 = PremisAgentTest(1)
    test_agent2 = PremisAgentTest(2)
    sip_meta = SipMetadata()
    sip_meta.add_agent(test_agent1)
    sip_meta.add_agent(test_agent2)
    sip_meta.add_agent(test_agent1)  # Duplicate, not added
    assert len(sip_meta.premis_agents) == 2
    assert sip_meta.premis_agents[1]
    assert sip_meta.premis_agents[2]

    count = 0
    for obj in sip_meta.agents:
        count = count + 1
    assert count == 2


def test_linkings():
    """Test that linkings can be added without duplicates.
    """
    linking1 = PremisLinkingTest(1)
    linking2 = PremisLinkingTest(2)
    sip_meta = SipMetadata()
    sip_meta.add_linking(linking1, 1, 2, "tester")
    sip_meta.add_linking(linking2, 3, 4, "tester")
    sip_meta.add_linking(linking1, 1, 2, "tester")  # Duplicate, not added
    assert len(sip_meta.premis_linkings) == 2
    assert sip_meta.premis_linkings[1]
    assert sip_meta.premis_linkings[2]

    count = 0
    for obj in sip_meta.linkings:
        count = count + 1
    assert count == 2


def test_add_object_link():
    """Test that object links can be added without duplicates.
    """
    linking = PremisLinking()
    linking.add_object_link(1)
    linking.add_object_link(2)
    linking.add_object_link(1)  # Duplicate, not added
    assert linking.object_links == [
        {"linking_object": 1}, {"linking_object": 2}]


def test_add_agent_link():
    """Test that agent links can be added without duplicates.
    """
    linking = PremisLinking()
    linking.add_agent_link(1, "tester")
    linking.add_agent_link(2, "improver")
    linking.add_agent_link(1, "tester")  # Duplicate, not added
    assert linking.agent_links == [
        {"linking_agent": 1, "agent_role": "tester"},
        {"linking_agent": 2, "agent_role": "improver"}]
