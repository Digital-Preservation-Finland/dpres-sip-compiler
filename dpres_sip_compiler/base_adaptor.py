"""
"""
class SipMeta(object):
    """
    """
    def __init__(self):

        self.premis_objects = {}
        self.premis_events = {}
        self.premis_agents = {}
        self.premis_linkings = {}

    def _add_premis(self, premis_elem, premis_dict):
        if premis_elem.identifier in premis_dict:
            return
        premis_dict[premis_elem.identifier] = premis_elem

    def add_object(self, p_object):
        self._add_premis(p_object, self.premis_objects)

    def add_event(self, p_event):
        self._add_premis(p_event, self.premis_events)

    def add_agent(self, p_agent):
        self._add_premis(p_agent, self.premis_agents)

    def add_linking(self, p_linking, object_id, agent_id, agent_role):
        self._add_premis(p_linking, self.premis_linkings)
        self.premis_linkings[p_linking.identifier].add_object(object_id)
        self.premis_linkings[p_linking.identifier].add_agent(
            agent_id, agent_role)

    @property
    def objects(self):
        for premis_object in self.premis_objects.values():
            yield premis_object

    @property
    def events(self):
        for premis_event in self.premis_events.values():
            yield premis_event

    @property
    def agents(self):
        for premis_agent in self.premis_agents.values():
            yield premis_agent

    @property
    def linkings(self):
        for premis_linking in self.premis_linkings.values():
            yield premis_linking


class PremisObject(object):
    """
    """

    def __init__(self, **kwargs):
        self.filepath = None

    @property
    def identifier(self):
        return self.object_identifier_value

    @property
    def object_identifier_type(self):
        return None

    @property
    def object_identifier_value(self):
        return None


class PremisEvent(object):
    """
    """

    @property
    def identifier(self):
        return self.event_identifier_value

    @property
    def event_identifier_type(self):
        return None

    @property
    def event_identifier_value(self):
        return None


class PremisAgent(object):
    """
    """

    @property
    def identifier(self):
        return self.agent_identifier_value

    @property
    def agent_identifier_type(self):
        return None

    @property
    def agent_identifier_value(self):
        return None


class PremisLinking(object):
    """
    """

    def __init__(self, **kwargs):
        """
        """
        self.identifier = None
        self.objects = []
        self.agents = []

    def add_object(self, identifier):
        if identifier in [obj["linking_object"] for obj in self.objects]:
            return
        self.objects.append({"linking_object": identifier})

    def add_agent(self, identifier, agent_role):
        if identifier in [agent["linking_agent"] for agent in self.agents]:
            return
        self.agents.append({"linking_agent": identifier,
                            "agent_role": agent_role})
