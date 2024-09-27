"""Compile SIP using dpres-siptools-ng."""

import os
from mets_builder import METS, MetsProfile
from mets_builder.metadata import ImportedMetadata

from siptools_ng.sip import SIP
from siptools_ng.file import File

from dpres_sip_compiler.base_adaptor import build_sip_metadata
from dpres_sip_compiler.adaptor_list import ADAPTOR_NG_DICT
from dpres_sip_compiler.config import Config, get_default_config_path


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class SipCompiler:
    """Class to compile SIP."""
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, source_path, descriptive_metadata_path,
                 config, tar_file, sip_meta):
        self.source_path = source_path
        self.descriptive_metadata_path = descriptive_metadata_path
        self.config = config
        self.tar_file = tar_file
        self.sip_meta = sip_meta
        self.mets = None
        self.digital_objects = []
        self.descriptive_metadata = None

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
            digital_object = File(
                path=obj.filepath,
                digital_object_path=os.path.relpath(
                    obj.filepath, self.source_path)
            )
            digital_object.generate_technical_metadata()
            self.digital_objects.append(digital_object)

    def _import_descriptive_metadata(self):
        """Import descriptive metadata from input descriptive metadata
        path.
        """
        self.descriptive_metadata = ImportedMetadata(
            data_path=self.descriptive_metadata_path,
            metadata_type="descriptive",
            metadata_format=self.config.desc_metadata_format,
            format_version=self.config.desc_metadata_version)

    def _finalize_sip(self):
        """Turn the METS object into a SIP."""

        sip = SIP.from_files(mets=self.mets, files=self.digital_objects)
        sip.add_metadata([self.descriptive_metadata])
        sip.finalize(
            output_filepath=self.tar_file,
            sign_key_filepath=self.config.sign_key
        )

    def create_sip(self):
        """Create SIP."""
        self._initialize_mets()
        self._create_technical_metadata()
        self._import_descriptive_metadata()
        self._finalize_sip()
        print(f"Compilation finished. The SIP is signed and packaged to: "
              f"{self.tar_file}.")


def ng_compile_sip(source_path, descriptive_metadata_path, tar_file,
                   conf_file=None):
    """Compile SIP."""
    if conf_file is None:
        conf_file = get_default_config_path()

    config = Config()
    config.configure(conf_file)

    sip_meta = build_sip_metadata(ADAPTOR_NG_DICT, source_path, config)
    compiler = SipCompiler(source_path=source_path,
                           descriptive_metadata_path=descriptive_metadata_path,
                           config=config,
                           tar_file=tar_file,
                           sip_meta=sip_meta)
    compiler.create_sip()
