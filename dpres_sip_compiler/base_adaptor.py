"""
Base adaptor for handling PREMIS metadata in packaging.

Adaptors can overwrite the required methods and properties as needed.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal, overload

from file_scraper.scraper import Scraper

if TYPE_CHECKING:
    from collections.abc import Iterator

    from lxml import etree as ET

    from dpres_sip_compiler.config import Config


def build_sip_metadata(adaptor_dict: dict,
                       source_path: str,
                       config: Config,
                       content_id: str | None = None,
                       sip_id: str | None = None) -> SipMetadata:
    """Build metadata object based on given class.

    :param adaptor_dict: Dict of adaptor names and corresponding SIP
        metadata classes.
    :param source_path: Source data path
    :param config: Basic configuration
    :returns: SIP metadata object
    """
    sip_meta = sip_metadata_class(adaptor_dict, config)()
    sip_meta.populate(source_path, config)

    if content_id:
        sip_meta.content_id = content_id
    if sip_id:
        sip_meta.objid = sip_id

    return sip_meta


def sip_metadata_class(adaptor_dict: dict[str, type[SipMetadata]],
                       config: Config) -> type[SipMetadata]:
    """Find metadata class for SIP based on configured adaptor.

    :param adaptor_dict: Dict of adaptor names and corresponding SIP
        metadata classes.
    :param config: Basic configuration
    :returns: SIP metadata class
    """
    if config.adaptor not in adaptor_dict:
        raise NotImplementedError(
            "Unsupported configuration! Maybe the adaptor name is incorrect "
            "in configuration file?")

    return adaptor_dict[config.adaptor]


class PremisObject:
    """Class for a PREMIS Object.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self, metadata: dict[str, str | bool | None]) -> None:
        """Initialize object.
        :param metadata: Metadata dict for object.
        """
        self.filepath = None  # File path to object
        self._metadata = metadata
        for key in [
            "object_identifier_type",
            "object_identifier_value",
            "original_name",
            "message_digest_algorithm",
            "message_digest",
            "bit_level",
        ]:
            if key not in self._metadata:
                self._metadata[key] = None
        self._metadata["bit_level"] = False

    @overload
    def __getattr__(self, attr: Literal["bit_level"]) -> bool: ...

    @overload
    def __getattr__(
        self,
        attr: Literal[
            "object_identifier_type",
            "object_identifier_value",
            "original_name",
            "message_digest_algorithm",
            "message_digest",
        ],
    ) -> str | None: ...
    @overload
    def __getattr__(self, attr: str) -> str | bool | None: ...

    def __getattr__(self, attr: str) -> str | bool | None:
        """
        Set metadata items as properties.
        :param attr: Attribute name
        :returns: Value for given attribute or None
        """
        return self._metadata.get(attr)

    @property
    def identifier(self) -> str | None:
        """Identifier of PREMIS Object, to be used as internal id.
        PREMIS objectIdentifierValue by default.
        """
        return self.object_identifier_value

    @property
    def format_name(self) -> str | None:
        """File format name."""
        # We have to give help with CSV files.
        # Automatic identifying recognizes CSV files as text files.
        if self.filepath is not None and self.filepath.endswith(".csv"):
            return "text/csv"
        return None

    @property
    def format_version(self) -> str | None:
        """File format version."""
        # We have to give help with CSV files.
        # Automatic identifying recognizes CSV files as text files.
        if self.filepath is not None and self.filepath.endswith(".csv"):
            return ""
        return None

    def remove_metadata(self, metadata_key: str) -> None:
        """Remove key from metadata."""
        self._metadata.pop(metadata_key, None)


class PremisEvent:
    """Class for a PREMIS Event.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self, metadata: dict[str, str | ET._Element | None]) -> None:
        """Initialize event.

        :param metadata: Metadata dict for event.
        """
        self._metadata = metadata
        for key in [
            "event_identifier_type",
            "event_identifier_value",
            "event_type",
            "event_outcome",
            "event_datetime",
            "event_detail",
            "event_outcome_detail",
            "event_outcome_detail_extension"
        ]:
            if key not in self._metadata:
                self._metadata[key] = None

    @overload
    def __getattr__(
        self, attr: Literal["event_outcome_detail_extension"]
    ) -> ET._Element | None: ...

    @overload
    def __getattr__(
        self,
        attr: Literal[
            "event_identifier_type",
            "event_identifier_value",
            "event_type",
            "event_outcome",
            "event_datetime",
            "event_detail",
            "event_outcome_detail",
        ],
    ) -> str | None: ...
    @overload
    def __getattr__(self, attr: str) -> str | ET._Element | None: ...

    def __getattr__(self, attr: str) -> str | ET._Element | None:
        """
        Set metadata items as properties.

        :param attr: Attribute name
        :returns: Value for given attribute or None
        """
        return self._metadata.get(attr)

    @property
    def identifier(self) -> str | None:
        """Identifier of PREMIS Event, to be used as internal id.
        PREMIS eventIdentifierValue by default.
        """
        return self.event_identifier_value

    def remove_metadata(self, metadata_key: str) -> str | None:
        """Remove key from metadata."""
        self._metadata.pop(metadata_key, None)


class PremisAgent:
    """Class for a PREMIS Agent.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self, metadata: dict[str, str | None]) -> None:
        """Initialize agent.
        :param metadata: Metadata dict for agent.
        """
        self._metadata = metadata
        for key in [
            "agent_identifier_type",
            "agent_identifier_value",
            "agent_name",
            "agent_type",
        ]:
            if key not in self._metadata:
                self._metadata[key] = None

    def __getattr__(self, attr: str) -> str | None:
        """
        Set metadata items as properties.
        :param attr: Attribute name
        :returns: Value for given attribute or None
        """
        if attr in self._metadata:
            return self._metadata[attr]

        return None

    @property
    def identifier(self) -> str | None:
        """Identifier of PREMIS Agent, to be used as internal id.
        PREMIS agentIdentifierValue by default.
        """
        return self.agent_identifier_value

    def remove_metadata(self, metadata_key: str) -> None:
        """Remove key from metadata."""
        self._metadata.pop(metadata_key, None)


class PremisLinking:
    """Class for a PREMIS Linking.
    Can be overwritten with metadata type specific adaptors.
    """

    def __init__(self):
        """Initialize Linking."""
        self.identifier: str | None = None  # Identifier of the linking
        self.object_links: list[dict[str, str]] = []  # List of object IDs
        self.agent_links: list[
            dict[str, str]
        ] = []  # List of agent IDs and roles

    def add_object_link(self, identifier: str, object_role: str) -> None:
        """Add object and its role to linking, if it does not exist.

        :identifier: Object ID to be added.
        :object_role: Object role to be added.
        """
        if identifier is None:
            return
        for obj in self.object_links:
            if identifier == obj["linking_object"]:
                return
        self.object_links.append(
            {"linking_object": identifier, "object_role": object_role}
        )

    def add_agent_link(self, identifier: str, agent_role: str) -> None:
        """Add agent to linking, if it does not exist.

        :identifier: Agent ID to be added.
        :agent_role: Role of the agent in linking.
        """
        if identifier is None:
            return
        for agent in self.agent_links:
            if identifier == agent["linking_agent"]:
                return
        self.agent_links.append(
            {"linking_agent": identifier, "agent_role": agent_role}
        )


class SipMetadata:
    """
    Metadata handler for a SIP to be compiled.
    Can be overwritten with metadata type specific adaptors.

    Attributes:
        objid: METS objid
        premis_objects: Dictionary of PREMIS Objects
        premis_events: Dictionary of PREMIS Events
        premis_agents: Dictionary of PREMIS Agents
        premis_linkings: Dictionary of Linkings inside PREMIS
        premis_digiprov_representations: Dictionary of PREMIS
            Representations as digiprov MD

    """

    # pylint: disable=no-self-use

    def __init__(self) -> None:
        """Initialize SIP PREMIS handler."""
        self.content_id: str | None = None
        self.objid: str | None = None
        self.premis_objects: dict[str, PremisObject] = {}
        self.premis_object_alt_ids: dict[str, list[dict[str, str]]] = {}
        self.premis_events: dict[str, PremisEvent] = {}
        self.premis_agents: dict[str, PremisAgent] = {}
        self.premis_linkings: dict[str, PremisLinking] = {}
        # To store possible object representations, may include
        # redundant information, but the information has to
        # be available for lookup when generation digiprov information
        # and actual object file is missing.
        self.premis_digiprov_representations = {}
        # To store scraper result.
        self.scraper_results = {}
        # To enforce specific attributes to the digital object
        # regardless what other tools claim these values are.
        self.digital_object_attributes = {}

    def populate(self, source_path, config):
        """Create metadata objects based on source path."""
        pass

    def descriptive_metadata_sources(
        self,
        desc_paths: list[str],
        config: Config,
    ) -> Iterator[tuple[str, str]]:
        """
        Iterator for descriptive metadata sources.
        Yields tuples of data source format and given metadata file
        paths.

        :param desc_paths: A list of descriptive metadata paths
        :param config: Additional needed configuration
        :returns: Iterator with tuple of descriptive metadata source
            format and file
        """
        for metadata_path in desc_paths:
            yield (config.desc_metadata_source_format, metadata_path)

    @staticmethod
    def exclude_files(config: Config) -> tuple[str, ...]:
        """
        Exclude files from Submission Information Package.
        Implemented in adaptors.

        :param config: Additional needed configuration
        :returns: Patterns for metadata files to be excluded.
        """
        return ()

    def scrape_objects(self, source_path: str, validation: bool) -> None:
        """To scrape objects and store their scraper results.

        :param source_path: Source path for the objects.
        :param validation: Whether to enable well_formed check or not.
        """
        for obj_identifier, obj in self.premis_objects.items():
            scraper = Scraper(
                filename=os.path.join(source_path, obj.filepath),
                mimetype=obj.format_name,
                version=obj.format_version,
            )
            scraper.scrape(check_wellformed=validation)
            scraper_result = {
                "streams": scraper.streams,
                "info": scraper.info,
                "mimetype": scraper.mimetype,
                "version": scraper.version,
                "checksum": scraper.checksum().lower(),
                "grade": scraper.grade(),
            }
            self.scraper_results[obj_identifier] = scraper_result

    def add_object(self, p_object: PremisObject) -> None:
        """Add PREMIS Object. Do not add if already exists.

        :param p_object: PREMIS Object
        """
        if p_object.identifier not in self.premis_objects:
            self.premis_objects[p_object.identifier] = p_object

    def add_object_alt_id(
        self,
        obj_identifier: str,
        alt_identifier_type: str,
        alt_identifier: str,
    ) -> None:
        """Add additional unique alternative ID for the object.

        :param obj_identifier: Main identifier of the object.
        :param alt_identifier_type: Alternative identifier type for the object.
        :param alt_identifier: Alternative identifier for the object.
        """
        if obj_identifier not in self.premis_object_alt_ids:
            self.premis_object_alt_ids[obj_identifier] = []
        new_alt = {
            "alt_identifier_type": alt_identifier_type,
            "alt_identifier": alt_identifier,
        }
        if new_alt not in self.premis_object_alt_ids[obj_identifier]:
            self.premis_object_alt_ids[obj_identifier].append(new_alt)

    def add_object_attribute(
        self, obj_identifier: str, name: str, value: str
    ) -> None:
        """Add additional attribute to the given digital object that would be
        used after pre-processing of the object is done.

        :param obj_identifier: Main identifier of the object.
        :param name: Name of the attribute.
        :param value: Value of the attribute.
        """
        if obj_identifier not in self.digital_object_attributes:
            self.digital_object_attributes[obj_identifier] = {}
        self.digital_object_attributes[obj_identifier][name] = value

    def add_event(self, p_event: PremisEvent) -> None:
        """Add PREMIS Event. Do not add if already exists.

        :param p_event: PREMIS Event
        """
        if p_event.identifier not in self.premis_events:
            self.premis_events[p_event.identifier] = p_event

    def add_agent(self, p_agent: PremisAgent) -> None:
        """Add PREMIS Agent. Do not add if already exists.

        :param p_agent: PREMIS Agent
        """
        if p_agent.identifier not in self.premis_agents:
            self.premis_agents[p_agent.identifier] = p_agent

    def add_linking(
        self,
        p_linking: PremisLinking,
        object_id: str,
        object_role: str,
        agent_id: str,
        agent_role: str,
    ) -> None:
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

        :param p_linking: Linking object
        :param object_id: PREMIS Object ID
        :param object_role: PREMIS Object role in event
        :param agent_id: PREMIS Agent ID
        :param agent_role: Role of the PREMIS Agent in linking
        """
        if p_linking.identifier not in self.premis_linkings:
            self.premis_linkings[p_linking.identifier] = p_linking

        self.premis_linkings[p_linking.identifier].add_object_link(
            object_id, object_role
        )
        self.premis_linkings[p_linking.identifier].add_agent_link(
            agent_id, agent_role
        )

    def add_digiprov_representation_object(self, p_object):
        """
        Add PREMIS representation object to a dict.

        :p_object: PREMIS representation object
        """
        if p_object.identifier not in self.premis_digiprov_representations:
            self.premis_digiprov_representations[p_object.identifier] = []
        self.premis_digiprov_representations[p_object.identifier].append(
            p_object)

    @property
    def objects(self) -> Iterator[PremisObject]:
        """Iterate PREMIS Objects.
        :returns: PREMIS Object
        """
        yield from self.premis_objects.values()

    @property
    def events(self) -> Iterator[PremisEvent]:
        """Iterate PREMIS Events.
        :returns: PREMIS Event
        """
        yield from self.premis_events.values()

    @property
    def agents(self) -> Iterator[PremisAgent]:
        """Iterate PREMIS Agents.
        :returns: PREMIS Agent
        """
        yield from self.premis_agents.values()

    @property
    def linkings(self) -> Iterator[PremisLinking]:
        """Iterate PREMIS Linkings.
        :returns: PREMIS Linking
        """
        yield from self.premis_linkings.values()
