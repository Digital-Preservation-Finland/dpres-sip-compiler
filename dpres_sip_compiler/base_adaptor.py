"""
Base adaptor for handling PREMIS metadata in packaging.

Adaptors can overwrite the required methods and properties as needed.
"""


def build_sip_metadata(adaptor_dict, source_path, config):
    """
    Build metadata object based on given class.
    :adaptor_dict: Dict of adaptor names and corresponding SIP metadata
                   classes.
    :source_path: Source data path
    :config: Basic configuration
    :returns: SIP metadata object
    """
    if config.adaptor not in adaptor_dict:
        raise NotImplementedError(
            "Unsupported configuration! Maybe the adaptor name is incorrect "
            "in configuration file?")

    sip_meta = adaptor_dict[config.adaptor]()
    sip_meta.populate(source_path, config)
    return sip_meta


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


class SipMetadata(object):
    """
    Metadata handler for a SIP to be compiled.
    Can be overwritten with metadata type specific adaptors.
    """

    # pylint: disable=no-self-use

    def __init__(self):
        """
        Initialize SIP PREMIS handler.
        """
        self.objid = None           # METS OBJID
        self.premis_objects = {}    # PREMIS Objects
        self.premis_events = {}     # PREMIS Events
        self.premis_agents = {}     # PREMIS Agents
        self.premis_linkings = {}   # Linkings inside PREMIS

    def populate(self, source_path, config):
        """Create metadata objects based on source path.
        """
        pass

    # pylint: disable=unused-argument
    def descriptive_files(self, desc_path, config):
        """
        Iterator for descriptive metadata files.
        Implemented in adaptors.

        :desc_path: Path to descriptive metadata files
        :config: Additional needed configuration
        :returns: Descriptive metadata file
        """
        yield

    # pylint: disable=unused-argument
    def desc_root_remove(self, config):
        """
        Resolve whether descriptive metadata root should be removed.
        Implemented in adaptors.

        :config: Additional needed configuration
        :returns: True/False
        """
        return False

    # pylint: disable=unused-argument
    def exclude_files(self, config):
        """
        Exclude files from Submission Information Package.
        Implemented in adaptors.

        :config: Additional needed configuration
        :returns: Patterns for metadata files to be excluded.
        """
        return ()

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

        The links are appended to a dict structure: A key in a link is an
        event identifier, and the corresponding value contains identifiers of
        the PREMIS objects and agents, which are related to the event.

        This method adds linkings between a PREMIS event, and a PREMIS object
        and agent. More objects/agent can be added with multiple calls: If
        the key (i.e. event identifier) exists already, the method appends
        the given PREMIS object and agent linkings along with the existing
        ones.

        :p_linking: Linking object
        :object_id: PREMIS Object ID
        :agent_id: PREMIS Agent ID
        :agent_role: Role of the PREMIS Agent in linking
        """
        add_premis(p_linking, self.premis_linkings)
        self.premis_linkings[p_linking.identifier].add_object_link(object_id)
        self.premis_linkings[p_linking.identifier].add_agent_link(
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

    # pylint: disable=no-self-use

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

    @property
    def original_name(self):
        """Original name.
        """
        return None

    @property
    def message_digest_algorithm(self):
        """Checksum algorithm.
        """
        return None

    @property
    def message_digest(self):
        """Checksum.
        """
        return None

    @property
    def format_name(self):
        """File format name
        """
        # We have to give help with CSV files.
        # Automatic identifying recognizes CSV files as text files.
        if self.filepath.endswith(".csv"):
            return "text/csv"
        return None

    @property
    def format_version(self):
        """File format version
        """
        # We have to give help with CSV files.
        # Automatic identifying recognizes CSV files as text files.
        if self.filepath.endswith(".csv"):
            return ""
        return None


class PremisEvent(object):
    """Class for a PREMIS Event.
    Can be overwritten with metadata type specific adaptors.
    """

    # pylint: disable=no-self-use

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

    @property
    def event_type(self):
        """Event type.
        """
        return None

    @property
    def event_datetime(self):
        """Event datetime.
        """
        return None

    @property
    def event_detail(self):
        """Event detail.
        """
        return None

    @property
    def event_outcome(self):
        """Event outcome.
        """
        return None

    @property
    def event_outcome_detail(self):
        """Event outcome detail.
        """
        return None


class PremisAgent(object):
    """Class for a PREMIS Event.
    Can be overwritten with metadata type specific adaptors.
    """

    # pylint: disable=no-self-use

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

    @property
    def agent_name(self):
        """Agent name.
        """
        return None

    @property
    def agent_type(self):
        """Agent type.
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
        self.object_links = []  # List of object IDs
        self.agent_links = []   # List of agent IDs and roles

    def add_object_link(self, identifier):
        """Add object to linking, if it does not exist.

        :identifier: Object ID to be added.
        """
        if identifier is None:
            return
        for obj in self.object_links:
            if identifier == obj["linking_object"]:
                return
        self.object_links.append({"linking_object": identifier})

    def add_agent_link(self, identifier, agent_role):
        """Add agent to linking, if it does not exist.

        :identifier: Agent ID to be added.
        :agent_role: Role of the agent in linking.
        """
        if identifier is None:
            return
        for agent in self.agent_links:
            if identifier == agent["linking_agent"]:
                return
        self.agent_links.append({"linking_agent": identifier,
                                 "agent_role": agent_role})
