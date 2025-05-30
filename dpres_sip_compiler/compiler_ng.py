"""Compile SIP using dpres-siptools-ng."""

import os
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
from file_scraper.defaults import BIT_LEVEL_WITH_RECOMMENDED

from dpres_sip_compiler.base_adaptor import build_sip_metadata
from dpres_sip_compiler.adaptor_list import ADAPTOR_NG_DICT
from dpres_sip_compiler.config import Config, get_default_config_path

OUTCOME = "outcome"
SOURCE = "source"
TARGET = "target"


def _get_technical_file_object_metadata(
    obj: File,
) -> TechnicalFileObjectMetadata:
    """Fetch TechnicalFileObjectMetadata from File-object.
    :param obj: File object that has technical file object metadata
        generated.
    :returns: TechnicalFileObjectMetadata object otherwise None if no such
        thing exists.
    """
    for metadata in obj.digital_object.metadata:
        if isinstance(metadata, TechnicalFileObjectMetadata):
            return metadata


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class SipCompiler:
    """Class to compile SIP."""

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, source_path, descriptive_metadata_paths,
                 config, tar_file, sip_meta, validation):
        self.source_path = source_path
        self.descriptive_metadata_paths = []
        if descriptive_metadata_paths:
            self.descriptive_metadata_paths = descriptive_metadata_paths
        self.config = config
        self.validation = validation
        self.tar_file = tar_file
        self.sip_meta = sip_meta
        self.mets = None
        self.digital_objects = {}
        self.representative_objects = {}
        self.event_metadata = []
        self.descriptive_metadata = []

    def _get_repsentation_object(
        self, object_id: str
    ) -> TechnicalRepresentationObjectMetadata:
        """Shorthand function to return the representation object, but
        if one doesn't exist then set it up before returning the object.

        :param object_id: Object identifier of the representation object
            to return.
        :return: TechnicalRepresentationObjectMetadata object.
        """
        try:
            return self.representative_objects[object_id]
        except KeyError:
            pass

        try:
            repr_obj = self.sip_meta.premis_digiprov_representations[
                object_id
            ][0]
            object_metadata = TechnicalRepresentationObjectMetadata(
                object_identifier_type=repr_obj.object_identifier_type,
                object_identifier=object_id,
                original_name=repr_obj.original_name,
            )
        except KeyError:
            # If for some reason representation was missing...
            object_metadata = TechnicalRepresentationObjectMetadata(
                object_identifier_type="UUID",
                object_identifier=object_id,
            )

        try:
            # Setup alternative IDs if possible.
            for alt_id in self.sip_meta.premis_object_alt_ids[object_id]:
                object_metadata.add_alternative_identifier(
                    identifier_type=alt_id["alt_identifier_type"],
                    identifier=alt_id["alt_identifier"],
                )
        except KeyError:
            pass

        self.representative_objects[object_id] = object_metadata
        return object_metadata

    def _scrape_objects(self) -> None:
        """Scrape objects."""
        self.sip_meta.scrape_objects(
            source_path=self.source_path,
            validation=self.validation,
        )

    def _initialize_mets(self):
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

    def _create_technical_metadata(self):
        """Create digital objects and add metadata to them."""
        for obj_identifier, obj in self.sip_meta.premis_objects.items():
            digital_object = File(
                path=os.path.join(self.source_path, obj.filepath),
                digital_object_path=obj.filepath,
            )
            digital_object.generate_technical_metadata(
                checksum=obj.message_digest,
                checksum_algorithm=obj.message_digest_algorithm,
                object_identifier=obj.object_identifier_value,
                object_identifier_type=obj.object_identifier_type,
                original_name=obj.original_name,
                scraper_result=self.sip_meta.scraper_results[obj_identifier],
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
                        obj=self.digital_objects[object_link["linking_object"]]
                    )
                    if obj_role not in [SOURCE, OUTCOME]:
                        obj_role = TARGET
                    if obj_role == SOURCE:
                        # Objects being in normalization or migration
                        # will have bit_level enforced
                        self.digital_objects[
                            object_link["linking_object"]
                        ].digital_object.use = BIT_LEVEL_WITH_RECOMMENDED
                    self.digital_objects[
                        object_link["linking_object"]
                    ].add_metadata([event_metadata])
                except KeyError:
                    object_metadata = self._get_repsentation_object(
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

    def _finalize_sip(self):
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

    def create_sip(self):
        """Create SIP."""
        self._scrape_objects()
        self._initialize_mets()
        self._create_technical_metadata()
        self._create_provenance_metadata()
        self._setup_alternative_object_ids()
        self._import_descriptive_metadata()
        self._finalize_sip()
        print(f"Compilation finished. The SIP is signed and packaged to: "
              f"{self.tar_file}.")


def ng_compile_sip(source_path,
                   tar_file,
                   descriptive_metadata_paths=None,
                   conf_file=None,
                   validation=True):
    """Compile SIP."""
    if conf_file is None:
        conf_file = get_default_config_path()

    config = Config(conf_file=conf_file)

    sip_meta = build_sip_metadata(ADAPTOR_NG_DICT, source_path, config)
    compiler = SipCompiler(
        source_path=source_path,
        descriptive_metadata_paths=descriptive_metadata_paths,
        config=config,
        tar_file=tar_file,
        sip_meta=sip_meta,
        validation=validation,
    )
    compiler.create_sip()
