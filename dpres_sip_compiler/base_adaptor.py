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

    def add_object(self, info):
        pass

    def add_agent(self, info):
        pass
