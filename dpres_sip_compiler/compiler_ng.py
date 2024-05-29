"""Example code for manual SIP creation."""

import os
from mets_builder import METS, MetsProfile, StructuralMap
from mets_builder.metadata import ImportedMetadata

from siptools_ng.sip import SIP
from siptools_ng.sip_digital_object import SIPDigitalObject

from dpres_sip_compiler.base_adaptor import build_sip_metadata
from dpres_sip_compiler.adaptor_list import ADAPTOR_NG_DICT
from dpres_sip_compiler.config import Config, get_default_config_path


OUTPUT_SIP_PATH = "workspace/example-manual-sip.tar"


class SipCompiler:
    """Class to compile SIP."""

    def __init__(self, source_path, descriptive_metadata_path,
                 config, sip_meta):
        self.source_path = source_path
        self.descriptive_metadata_path = descriptive_metadata_path
        self.config = config
        self.sip_meta = sip_meta
        self.mets = None
        self.digital_objects = []
        self.descriptive_metadata = None
        self.structural_map = None

    def _initialize_mets(self):
        """Initialize dpres-mets-builder METS object with your
        information.
        """
        self.mets = METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            contract_id=self.config.contract,
            creator_name=self.config.name,
            creator_type="ORGANIZATION"
        )

    def _create_technical_metadata(self):
        """Create digital objects and add metadata to them."""
        for obj in self.sip_meta.objects:
            print()
            print(obj.filepath)
            print()
            digital_object = SIPDigitalObject(
                source_filepath=obj.filepath,
                sip_filepath=os.path.relpath(obj.filepath, self.source_path)
            )
            digital_object.generate_technical_metadata()
            self.digital_objects.append(digital_object)

    def _import_descriptive_metadata(self):
        """Import descriptive metadata from input descriptive metadata
        path (this one is in Dublin Core format).
        """
        self.descriptive_metadata = ImportedMetadata(
            data_path=self.descriptive_metadata_path,
            metadata_type="descriptive",
            metadata_format=self.config.desc_metadata_format,
            format_version=self.config.desc_metadata_version)

    def _compile_structural_map(self):
        """Create directory based structural map and add the imported
        descriptive metadata to it.
        """
        self.structural_map = StructuralMap.from_directory_structure(
            self.digital_objects)
        self.mets.add_structural_map(self.structural_map)
        self.structural_map.root_div.add_metadata(self.descriptive_metadata)

    def _finalize_sip(self):
        """Turn the METS object into a SIP."""
        sip = SIP(mets=self.mets)
        sip.finalize(
            output_filepath=OUTPUT_SIP_PATH,
            sign_key_filepath=self.config.sign_key
        )

    def create_sip(self):
        """Create SIP."""

        self._initialize_mets()
        self._create_technical_metadata()
        self._import_descriptive_metadata()
        self._compile_structural_map()
        self.mets.generate_file_references()
        self._finalize_sip()


def ng_compile_sip(source_path, descriptive_metadata_path, conf_file=None):
    """Compile SIP."""
    if conf_file is None:
        conf_file = get_default_config_path()

    config = Config()
    config.configure(conf_file)

    sip_meta = build_sip_metadata(ADAPTOR_NG_DICT, source_path, config)
    compiler = SipCompiler(source_path=source_path,
                           descriptive_metadata_path=descriptive_metadata_path,
                           config=config,
                           sip_meta=sip_meta)
    compiler.create_sip()
