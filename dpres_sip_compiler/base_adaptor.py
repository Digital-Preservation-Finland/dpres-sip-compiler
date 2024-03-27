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
    sip_meta = sip_metadata_class(adaptor_dict, config)()
    sip_meta.populate(source_path, config)
    return sip_meta


def sip_metadata_class(adaptor_dict, config):
    """
    Find metadata class for SIP based on configured adaptor.
    :adaptor_dict: Dict of adaptor names and corresponding SIP metadata
                   classes.
    :config: Basic configuration
    """
    if config.adaptor not in adaptor_dict:
        raise NotImplementedError(
            "Unsupported configuration! Maybe the adaptor name is incorrect "
            "in configuration file?")

    return adaptor_dict[config.adaptor]


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


class SipMetadata:
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

    @staticmethod
    def exclude_files(config):
        """
        Exclude files from Submission Information Package.
        Implemented in adaptors.

        :config: Additional needed configuration
        :returns: Patterns for metadata files to be excluded.
        """
        return ()

    def post_tasks(self, workspace, source_path):
        """
        Post tasks to workspace not supported by dpres-siptools.

        :workspace: Workspace path
        :source_path: Source path of files to be packaged
        """
        pass

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

    def add_linking(self, p_linking, object_id, object_role,
                    agent_id, agent_role):
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
        :object_role: PREMIS Object role in event
        :agent_id: PREMIS Agent ID
        :agent_role: Role of the PREMIS Agent in linking
        """
        add_premis(p_linking, self.premis_linkings)
        self.premis_linkings[p_linking.identifier].add_object_link(
            object_id, object_role)
        self.premis_linkings[p_linking.identifier].add_agent_link(
            agent_id, agent_role)

    @property
    def objects(self):
        """Iterate PREMIS Objects.
        :returns: PREMIS Object
        """
        yield from self.premis_objects.values()

    @property
    def events(self):
        """Iterate PREMIS Events.
        :returns: PREMIS Event
        """
        yield from self.premis_events.values()

    @property
    def agents(self):
        """Iterate PREMIS Agents.
        :returns: PREMIS Agent
        """
        yield from self.premis_agents.values()

    @property
    def linkings(self):
        """Iterate PREMIS Linkings.
        :returns: PREMIS Linking
        """
        yield from self.premis_linkings.values()


class PremisObject:
    """Class for a PREMIS Object.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self, metadata):
        """Initialize object.
        :metadata: Metadata dict for object.
        """
        self.filepath = None  # File path to object
        self._metadata = metadata
        for key in ["object_identifier_type",
                    "object_identifier_value",
                    "original_name",
                    "message_digest_algorithm",
                    "message_digest",
                    "bit_level"]:
            if key not in self._metadata:
                self._metadata[key] = None

    def __getattr__(self, attr):
        """
        Set metadata items as properties.
        :attr: Attribute name
        :returns: Value for given attribute or None
        """
        if attr in self._metadata:
            return self._metadata[attr]

        return None

    @property
    def identifier(self):
        """Identifier of PREMIS Object, to be used as internal id.
        PREMIS objectIdentifierValue by default.
        """
        return self.object_identifier_value

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

    def remove_metadata(self, metadata_key):
        """Remove key from metadata.
        """
        self._metadata.pop(metadata_key, None)


class PremisEvent:
    """Class for a PREMIS Event.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self, metadata):
        """Initialize event.
        :metadata: Metadata dict for event.
        """
        self._metadata = metadata
        for key in ["event_identifier_type",
                    "event_identifier_value",
                    "event_type",
                    "event_outcome",
                    "event_datetime",
                    "event_detail",
                    "event_outcome_detail"]:
            if key not in self._metadata:
                self._metadata[key] = None

    def __getattr__(self, attr):
        """
        Set metadata items as properties.
        :attr: Attribute name
        :returns: Value for given attribute or None
        """
        if attr in self._metadata:
            return self._metadata[attr]

        return None

    @property
    def identifier(self):
        """Identifier of PREMIS Event, to be used as internal id.
        PREMIS eventIdentifierValue by default.
        """
        return self.event_identifier_value

    def remove_metadata(self, metadata_key):
        """Remove key from metadata.
        """
        self._metadata.pop(metadata_key, None)


class PremisAgent:
    """Class for a PREMIS Agent.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self, metadata):
        """Initialize agent.
        :metadata: Metadata dict for agent.
        """
        self._metadata = metadata
        for key in ["agent_identifier_type",
                    "agent_identifier_value",
                    "agent_name",
                    "agent_type"]:
            if key not in self._metadata:
                self._metadata[key] = None

    def __getattr__(self, attr):
        """
        Set metadata items as properties.
        :attr: Attribute name
        :returns: Value for given attribute or None
        """
        if attr in self._metadata:
            return self._metadata[attr]

        return None

    @property
    def identifier(self):
        """Identifier of PREMIS Agent, to be used as internal id.
        PREMIS agentIdentifierValue by default.
        """
        return self.agent_identifier_value

    def remove_metadata(self, metadata_key):
        """Remove key from metadata.
        """
        self._metadata.pop(metadata_key, None)


class PremisLinking:
    """Class for a PREMIS Linking.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self):
        """Initialize Linking.
        """
        self.identifier = None  # Identifier of the linking
        self.object_links = []  # List of object IDs
        self.agent_links = []   # List of agent IDs and roles

    def add_object_link(self, identifier, object_role):
        """Add object and its role to linking, if it does not exist.

        :identifier: Object ID to be added.
        :object_role: Object role to be added.
        """
        if identifier is None:
            return
        for obj in self.object_links:
            if identifier == obj["linking_object"]:
                return
        self.object_links.append({"linking_object": identifier,
                                  "object_role": object_role})

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
