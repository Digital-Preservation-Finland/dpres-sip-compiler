"""
"""

class TestPremisObject(PremisObject):
    """
    """
    def __init__(self, identifier)
        """
        """
        self.identifier = identifier

    def identifier():
        """
        """
        return identifier


class TestPremisEvent():
    """
    """
    def __init__(self, identifier)
        """
        """
        self.identifier = identifier

    def identifier():
        """
        """
        return identifier


class TestPremisAgent():
    """
    """
    def __init__(self, identifier)
        """
        """
        self.identifier = identifier

    def identifier():
        """
        """
        return identifier


class TestPremisLinking():
    """
    """
    def __init__(self, identifier)
        """
        """
        self.identifier = identifier


def test_objects():
    """
    """
    test_object1 = TestPremisObject(1)
    test_object2 = TestPremisObject(2)
    sip_meta = SipMetadata()
    sip_meta.add_object(test_object1)
    sip_meta.add_object(test_object2)
    sip_meta.add_object(test_object1)
    assert len(sip_meta.premis_objects) == 2
    assert sip_meta.premis_objects[1]
    assert sip_meta.premis_objects[2]

    count = 0
    for obj in sip_meta.objects:
        count = count + 1
    assert count = 2


def test_events():
    """
    """
    test_event1 = TestPremisEvent(1)
    test_event2 = TestPremisEvent(2)
    sip_meta = SipMetadata()
    sip_meta.add_event(test_event1)
    sip_meta.add_event(test_event2)
    sip_meta.add_event(test_event1)
    assert len(sip_meta.premis_events) == 2
    assert sip_meta.premis_events[1]
    assert sip_meta.premis_events[2]

    count = 0
    for obj in sip_meta.events:
        count = count + 1
    assert count = 2


def test_agents():
    """
    """
    test_event1 = TestPremisAgent(1)
    test_event2 = TestPremisAgent(2)
    sip_meta = SipMetadata()
    sip_meta.add_agent(test_agent1)
    sip_meta.add_agent(test_agent2)
    sip_meta.add_agent(test_agent1)
    assert len(sip_meta.premis_agents) == 2
    assert sip_meta.premis_agents[1]
    assert sip_meta.premis_agents[2]

    count = 0
    for obj in sip_meta.agents:
        count = count + 1
    assert count = 2


def test_linkings():
    """
    """
    linking1 = TestPremisLinking(1)
    linking2 = TestPremisLinking(1)
    sip_meta = SipMetadata()
    sip_meta.add_linking(linking1, 1, 2, "target")
    sip_meta.add_linking(linking2, 3, 4, "target")
    sip_meta.add_linking(linking1, 1, 2, "target")
    assert len(sip_meta.premis_linkings) == 2
    assert sip_meta.premis_linkings[1]
    assert sip_meta.premis_linkings[2]

    count = 0
    for obj in sip_meta.linkings:
        count = count + 1
    assert count = 2


def test_add_object_link():
    """
    """
    linking = PremisLinking()
    linking.add_object_link(1)
    linking.add_object_link(2)
    linking.add_object_link(1)  # Not added
    assert linking.object_links = [
        {"linking_object": 1}, {"linking_object", 2}]


def test_add_agent_link():
    """
    """
    linking = PremisLinking()
    linking.add_agent_link(1, "target")
    linking.add_agent_link(2, "source")
    linking.add_agent_link(1, "outcome")  # Not added
    assert linking.agentt_links = [
        {"linking_agent": 1, "agent_role": "target"},
        {"linking_agent", 2, "agent_role": "source"}]
