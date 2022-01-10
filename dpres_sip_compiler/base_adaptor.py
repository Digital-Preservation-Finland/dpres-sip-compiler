"""
Base adaptor for handling PREMIS metadata in packaging.

Adaptors can overwrite the required methods and properties as needed.
"""

def add_premis(premis_elem, premis_dict):
    """
    Add PREMIS metadata object to a dict.
    Do not add if already exists.

    :premis_elem: PREMIS Element to be added to a dict
    :premis_dict: PREMIS dict
    """
    if premis_elem.identifier in premis_dict:
        return
    premis_dict[premis_elem.identifier] = premis_elem


class SipPremis(object):
    """
    PREMIS Metadata handler for a SIP to be compiled.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self):
        """
        Initialize SIP PREMIS handler.
        """

        self.premis_objects = {}    # PREMIS Objects
        self.premis_events = {}     # PREMIS Events
        self.premis_agents = {}     # PREMIS Agents
        self.premis_linkings = {}   # Linkings inside PREMIS

    def add_object(self, p_object):
        """Add PREMIS Object.
        :p_object: PREMIS Object
        """
        add_premis(p_object, self.premis_objects)

    def add_event(self, p_event):
        """Add PREMIS Event.
        :p_event: PREMIS Event
        """
        add_premis(p_event, self.premis_events)

    def add_agent(self, p_agent):
        """Add PREMIS Agent.
        :p_agent: PREMIS Agent
        """
        add_premis(p_agent, self.premis_agents)

    def add_linking(self, p_linking, object_id, agent_id, agent_role):
        """
        Create PREMIS linkings between events and objects/agents.

        Normally, the keys in linkings dict is same as event identifier, and
        the value contains identifiers to objects and agents. Create a new
        linking with creating a ne linking object referring to an event or
        append new object/agent linking to an existing linking object.

        :p_linking: Linking object
        :object_id: PREMIS Object ID
        :agent_id: PREMIS Agent ID
        :agent_role: Role of the PREMIS Agent in linking
        """
        add_premis(p_linking, self.premis_linkings)
        if object_id is not None:
            self.premis_linkings[p_linking.identifier].add_object(object_id)
        if agent_id is not None:
            self.premis_linkings[p_linking.identifier].add_agent(
                agent_id, agent_role)

    @property
    def objects(self):
        """Iterate PREMIS Objects.
        :returns: PREMIS Object
        """
        for premis_object in self.premis_objects.values():
            yield premis_object

    @property
    def events(self):
        """Iterate PREMIS Events.
        :returns: PREMIS Event
        """
        for premis_event in self.premis_events.values():
            yield premis_event

    @property
    def agents(self):
        """Iterate PREMIS Agents.
        :returns: PREMIS Agent
        """
        for premis_agent in self.premis_agents.values():
            yield premis_agent

    @property
    def linkings(self):
        """Iterate PREMIS Linkings.
        :returns: PREMIS Linking
        """
        for premis_linking in self.premis_linkings.values():
            yield premis_linking


class PremisObject(object):
    """Class for a PREMIS Object.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self):
        """Initialize object.
        """
        self.filepath = None  # File path to object

    @property
    def identifier(self):
        """Identifier of PREMIS Object, to be used as internal id.
        PREMIS objectIdentifierValue by default.
        """
        return self.object_identifier_value

    @property
    def object_identifier_type(self):
        """Value corresponding to PREMIS objectIdentifierType.
        """
        return None

    @property
    def object_identifier_value(self):
        """Value corresponding to PREMIS objectIdentifierValue.
        """
        return None


class PremisEvent(object):
    """Class for a PREMIS Event.
    Can be overwritten with metadata type specific adaptors.
    """

    @property
    def identifier(self):
        """Identifier of PREMIS Event, to be used as internal id.
        PREMIS eventIdentifierValue by default.
        """
        return self.event_identifier_value

    @property
    def event_identifier_type(self):
        """Value corresponding to PREMIS eventIdentifierType.
        """
        return None

    @property
    def event_identifier_value(self):
        """Value corresponding to PREMIS eventIdentifierValue.
        """
        return None


class PremisAgent(object):
    """Class for a PREMIS Event.
    Can be overwritten with metadata type specific adaptors.
    """

    @property
    def identifier(self):
        """Identifier of PREMIS Agent, to be used as internal id.
        PREMIS agentIdentifierValue by default.
        """
        return self.agent_identifier_value

    @property
    def agent_identifier_type(self):
        """Value corresponding to PREMIS agentIdentifierType.
        """
        return None

    @property
    def agent_identifier_value(self):
        """Value corresponding to PREMIS agentIdentifierValue.
        """
        return None


class PremisLinking(object):
    """Class for a PREMIS Linking.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self):
        """Initialize Linking.
        """
        self.identifier = None  # Identifier of the linking
        self.objects = []       # List of object IDs
        self.agents = []        # List of agent IDs and roles

    def add_object(self, identifier):
        """Add object to linking, if it does not exist.

        :identifier: Object ID to be added.
        """
        if identifier in [obj["linking_object"] for obj in self.objects]:
            return
        self.objects.append({"linking_object": identifier})

    def add_agent(self, identifier, agent_role):
        """Add agent to linking, if it does not exist.

        :identifier: Agent ID to be added.
        :agent_role: Role of the agent in linking.
        """
        if identifier in [agent["linking_agent"] for agent in self.agents]:
            return
        self.agents.append({"linking_agent": identifier,
                            "agent_role": agent_role})
