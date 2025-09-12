"""Compile SIP using dpres-siptools-ng."""

import os
from typing import List, Optional, Dict
from mets_builder import METS, MetsProfile
from mets_builder.metadata import (
    DigitalProvenanceAgentMetadata,
    DigitalProvenanceEventMetadata,
    ImportedMetadata,
    TechnicalFileObjectMetadata,
    TechnicalRepresentationObjectMetadata,
)

from siptools_ng.sip import SIP
from siptools_ng.file import File
from file_scraper.defaults import (
    ACCEPTABLE,
    BIT_LEVEL_WITH_RECOMMENDED,
    RECOMMENDED,
)

from dpres_sip_compiler.base_adaptor import build_sip_metadata, SipMetadata
from dpres_sip_compiler.adaptor_list import ADAPTOR_DICT
from dpres_sip_compiler.config import Config, get_default_config_path
from dpres_sip_compiler.constants import (
    EVENT_MIGRATION,
    EVENT_NORMALIZATION,
    FILE_USE_IGNORE_VALIDATION,
)

OUTCOME = "outcome"
SOURCE = "source"
TARGET = "target"


def _get_technical_file_object_metadata(
    obj: File,
) -> TechnicalFileObjectMetadata:
    """Return technical metadata object from a File object."""
    # Find the TechnicalFileObjectMetadata in the set
    for metadata in obj.metadata:
        if isinstance(metadata, TechnicalFileObjectMetadata):
            return metadata
    # Fallback if no TechnicalFileObjectMetadata found
    return list(obj.metadata)[0]


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class SipCompiler:
    """Class to compile SIP."""

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        source_path: str,
        descriptive_metadata_paths: Optional[List[str]],
        config: Config,
        tar_file: str,
        sip_meta: SipMetadata,
        validation: bool
    ) -> None:
        """Initialize SipCompiler instance.

        :param source_path: Path to the source directory containing files to
            package
        :param descriptive_metadata_paths: List of paths to descriptive
            metadata files, or None if no external descriptive metadata
        :param config: Configuration object containing SIP compilation settings
        :param tar_file: Path where the final SIP tar file will be created
        :param sip_meta: SIP metadata object containing PREMIS objects, events,
            and agents
        :param validation: Whether to perform file validation during
            compilation

        :returns: None
        """
        self.source_path = source_path
        self.descriptive_metadata_paths: List[str] = []
        if descriptive_metadata_paths:
            self.descriptive_metadata_paths = descriptive_metadata_paths
        self.config = config
        self.validation = validation
        self.tar_file = tar_file
        self.sip_meta = sip_meta
        self.mets: Optional[METS] = None
        self.digital_objects: Dict[str, File] = {}
        self.representative_objects: Dict[
            str, TechnicalRepresentationObjectMetadata
        ] = {}
        self.event_metadata: List[DigitalProvenanceEventMetadata] = []
        self.descriptive_metadata: List[ImportedMetadata] = []

    def _get_representation_object(
        self, object_id: str
    ) -> TechnicalRepresentationObjectMetadata:
        """Returns representation object metadata. Create the object
        if it does not exist.
        """
        if object_id in self.representative_objects:
            return self.representative_objects[object_id]

        # Check if premis_representation_objects exists before accessing it
        if hasattr(self.sip_meta, 'premis_representation_objects'):
            representation_object = (
                self.sip_meta.premis_representation_objects[object_id]
            )
            object_metadata = TechnicalRepresentationObjectMetadata(
                object_identifier_type=(
                    representation_object.object_identifier_type
                ),
                object_identifier=(
                    representation_object.object_identifier_value
                ),
            )

            # Create the related object metadata
            related_object_metadata = TechnicalRepresentationObjectMetadata(
                object_identifier_type=(
                    representation_object.related_object_identifier_type
                ),
                object_identifier=(
                    representation_object.related_object_identifier_value
                ),
            )

            object_metadata.add_relationship(
                technical_object_metadata=related_object_metadata,
                relationship_type=representation_object.relationship_type,
                relationship_subtype=(
                    representation_object.relationship_subtype
                ),
            )

            try:
                for alt_id in self.sip_meta.premis_object_alt_ids[object_id]:
                    object_metadata.add_alternative_identifier(
                        identifier_type=alt_id["alt_identifier_type"],
                        identifier=alt_id["alt_identifier"],
                    )
            except KeyError:
                pass

            self.representative_objects[object_id] = object_metadata
            return object_metadata
        else:
            object_metadata = TechnicalRepresentationObjectMetadata(
                object_identifier_type="UUID",
                object_identifier=object_id,
            )

            self.representative_objects[object_id] = object_metadata
            return object_metadata

    def _scrape_objects(self) -> None:
        """Scrape objects."""
        self.sip_meta.scrape_objects(
            source_path=self.source_path,
            validation=self.validation,
        )

    def _update_file_use_attributes(self):
        """Update USE attribute for source files in
        migration/normalization events.

        For source files in migration/normalization events:
        - ACCEPTABLE/RECOMMENDED grades: Marked as FILE_USE_IGNORE_VALIDATION
          (broken files that need content metadata skipped)
        - Other grades (UNACCEPTABLE, etc.): Marked as
          BIT_LEVEL_WITH_RECOMMENDED (bit-level preservation)
        """
        for obj_identifier, obj in self.sip_meta.premis_objects.items():
            if (
                obj_identifier in self.sip_meta.digital_object_attributes
                and self.sip_meta.digital_object_attributes[
                    obj_identifier
                ].get("use")
                == FILE_USE_IGNORE_VALIDATION
            ):
                continue

            if self._is_source_file_in_migration_normalization(obj_identifier):
                grade = self.sip_meta.scraper_results[obj_identifier]["grade"]
                if grade in (ACCEPTABLE, RECOMMENDED):
                    self.sip_meta.add_object_attribute(
                        obj_identifier=obj_identifier,
                        name="use",
                        value=FILE_USE_IGNORE_VALIDATION,
                    )
                else:
                    self.sip_meta.add_object_attribute(
                        obj_identifier=obj_identifier,
                        name="use",
                        value=BIT_LEVEL_WITH_RECOMMENDED,
                    )

    def _is_source_file_in_migration_normalization(
        self, obj_identifier: str
    ) -> bool:
        """Check if file is a source file in migration or normalization events.

        :param obj_identifier: Identifier of the digital object to check
        :returns: True if the file is a source file in any migration or
                  normalization event, False otherwise
        """
        for event in self.sip_meta.events:
            if event.event_type in [EVENT_MIGRATION, EVENT_NORMALIZATION]:
                try:
                    for object_link in self.sip_meta.premis_linkings[
                        event.identifier
                    ].object_links:
                        if (
                            object_link["linking_object"] == obj_identifier
                            and object_link["object_role"] == SOURCE
                        ):
                            return True
                except KeyError:
                    continue
        return False

    def _initialize_mets(self) -> None:
        """Initialize dpres-mets-builder METS object with your
        information.
        """
        self.mets = METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            contract_id=self.config.contract,
            creator_name=self.config.name,
            creator_type="ORGANIZATION",
            package_id=self.sip_meta.objid,
            content_id=self.sip_meta.content_id,
        )

    def _create_technical_metadata(self) -> None:
        """Create digital objects and add metadata to them."""
        for obj_identifier, obj in self.sip_meta.premis_objects.items():
            digital_object = File(
                path=os.path.join(self.source_path, obj.filepath),
                digital_object_path=obj.filepath,
            )

            skip_content_metadata = False
            if (
                obj_identifier in self.sip_meta.digital_object_attributes
                and "use" in self.sip_meta.digital_object_attributes[
                    obj_identifier
                ]
                and self.sip_meta.digital_object_attributes[obj_identifier][
                    "use"
                ]
                == FILE_USE_IGNORE_VALIDATION
            ):
                skip_content_metadata = True

            digital_object.generate_technical_metadata(
                checksum=obj.message_digest,
                checksum_algorithm=obj.message_digest_algorithm,
                object_identifier=obj.object_identifier_value,
                object_identifier_type=obj.object_identifier_type,
                original_name=obj.original_name,
                scraper_result=self.sip_meta.scraper_results[obj_identifier],
                skip_content_specific_metadata=skip_content_metadata,
            )
            self.digital_objects[obj_identifier] = digital_object

    def _create_provenance_metadata(self) -> None:
        """Create provenance metadata from representation objects,
        agents and events.
        """
        for event in self.sip_meta.events:
            event_metadata = DigitalProvenanceEventMetadata(
                event_type=event.event_type,
                detail=event.event_detail,
                outcome=event.event_outcome,
                outcome_detail=event.event_outcome_detail,
                datetime=event.event_datetime,
                event_identifier_type=event.event_identifier_type,
                event_identifier=event.event_identifier_value,
            )
            for agent_link in self.sip_meta.premis_linkings[
                event.identifier
            ].agent_links:
                agent = self.sip_meta.premis_agents[
                    agent_link["linking_agent"]
                ]
                agent_metadata = DigitalProvenanceAgentMetadata(
                    name=agent.agent_name,
                    agent_type=agent.agent_type,
                    agent_identifier_type=agent.agent_identifier_type,
                    agent_identifier=agent.agent_identifier_value,
                )
                event_metadata.link_agent_metadata(
                    agent_metadata=agent_metadata,
                    agent_role=agent_link["agent_role"],
                )

            for object_link in self.sip_meta.premis_linkings[
                event.identifier
            ].object_links:
                obj_role = object_link["object_role"]
                try:
                    object_metadata = _get_technical_file_object_metadata(
                        obj=self.digital_objects[
                            object_link["linking_object"]
                        ]
                    )
                    if obj_role not in [SOURCE, OUTCOME]:
                        obj_role = TARGET

                    self.digital_objects[
                        object_link["linking_object"]
                    ].add_metadata([event_metadata])
                except KeyError:
                    object_metadata = self._get_representation_object(
                        object_id=object_link["linking_object"]
                    )
                event_metadata.link_object_metadata(
                    object_metadata=object_metadata, object_role=obj_role
                )
            self.event_metadata.append(event_metadata)

    def _setup_alternative_object_ids(self) -> None:
        """Will add alternative IDs to the technical objects that were added.
        """
        for obj_id, obj in self.digital_objects.items():
            try:
                # Setup alternative IDs if possible.
                for alt_id in self.sip_meta.premis_object_alt_ids[obj_id]:
                    object_metadata = _get_technical_file_object_metadata(
                        obj=obj
                    )
                    object_metadata.add_alternative_identifier(
                        identifier_type=alt_id["alt_identifier_type"],
                        identifier=alt_id["alt_identifier"],
                    )
            except KeyError:
                pass

    def _override_object_attributes(self) -> None:
        """Will override digital object's attributes with pre-given
        value.
        """
        for (
            obj_id,
            obj_attributes,
        ) in self.sip_meta.digital_object_attributes.items():
            # We currently only support "use" overriding.
            try:
                self.digital_objects[obj_id].digital_object.use = (
                    obj_attributes["use"]
                )
            except KeyError:
                pass

    def _import_descriptive_metadata(self) -> None:
        """Import descriptive metadata from input descriptive metadata
        path.
        """
        metadata_paths = (
            list(
                self.sip_meta.descriptive_files(
                    desc_path=self.source_path, config=self.config
                )
            )
            + self.descriptive_metadata_paths
        )
        for metadata_path in metadata_paths:
            self.descriptive_metadata.append(
                ImportedMetadata(
                    data_path=metadata_path,
                    metadata_type="descriptive",
                    metadata_format=self.config.desc_metadata_format,
                    format_version=self.config.desc_metadata_version,
                )
            )

    def _finalize_sip(self) -> None:
        """Turn the METS object into a SIP."""

        sip = SIP.from_files(
            mets=self.mets,
            files=list(self.digital_objects.values()),
        )
        sip.add_metadata(self.event_metadata)
        sip.add_metadata(self.representative_objects.values())
        sip.add_metadata(self.descriptive_metadata)
        sip.finalize(
            output_filepath=self.tar_file,
            sign_key_filepath=self.config.sign_key
        )

    def create_sip(self) -> None:
        """Create SIP."""
        self._scrape_objects()
        self._initialize_mets()
        self._update_file_use_attributes()
        self._create_technical_metadata()
        self._create_provenance_metadata()
        self._setup_alternative_object_ids()
        self._override_object_attributes()
        self._import_descriptive_metadata()
        self._finalize_sip()
        print(f"Compilation finished. The SIP is signed and packaged to: "
              f"{self.tar_file}.")


def compile_sip(
    source_path: str,
    tar_file: str,
    descriptive_metadata_paths: Optional[List[str]] = None,
    conf_file: Optional[str] = None,
    validation: bool = True,
) -> None:
    """Compile SIP.

    :param source_path: Path to the source directory containing files to
        package
    :param tar_file: Path where the final SIP tar file will be created
    :param descriptive_metadata_paths: List of paths to descriptive metadata
        files, or None if no external descriptive metadata
    :param conf_file: Path to configuration file, or None to use default
    :param validation: Whether to perform file validation during compilation

    :returns: None
    """
    if conf_file is None:
        conf_file = get_default_config_path()

    config = Config(conf_file=conf_file)

    sip_meta = build_sip_metadata(ADAPTOR_DICT, source_path, config)
    compiler = SipCompiler(
        source_path=source_path,
        descriptive_metadata_paths=descriptive_metadata_paths,
        config=config,
        tar_file=tar_file,
        sip_meta=sip_meta,
        validation=validation,
    )
    compiler.create_sip()
