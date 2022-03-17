"""
Compile SIP based on a given metadata source.
Adaptors for different types of sources may be added.
"""
from __future__ import print_function

import os
import re
from siptools.scripts.import_object import import_object
from siptools.scripts.create_mix import create_mix
from siptools.scripts.create_videomd import create_videomd
from siptools.scripts.create_audiomd import create_audiomd
from siptools.scripts.create_addml import create_addml
from siptools.scripts.import_description import import_description
from siptools.scripts.premis_event import premis_event
from siptools.scripts.create_agent import create_agent
from siptools.scripts.compile_structmap import compile_structmap
from siptools.scripts.compile_mets import compile_mets
from siptools.scripts.sign_mets import sign_mets
from siptools.scripts.compress import compress
from siptools.utils import read_json_streams
from dpres_sip_compiler.config import Config, get_default_config_path
from dpres_sip_compiler.selector import select


# pylint: disable=too-few-public-methods
class SipCompiler(object):
    """Compiler to create SIPs
    """

    def __init__(self, workspace, config, sip_meta):
        """Initialize compiler.

        :workspace: Workspace path
        :config: Basic configuration
        :sip_meta: PREMIS metadata objects for the SIP to be compiled.
        """
        self.workspace = workspace
        self.config = config
        self.sip_meta = sip_meta

    def _create_technical_metadata(self):
        """Create technical metadata
        """
        print("Creating technical metadata for %d file(s)."
              "" % (len(self.sip_meta.premis_objects)))
        for obj in self.sip_meta.objects:
            file_format = ()
            if obj.filepath.endswith(".csv"):
                file_format = ("text/csv", "")
            import_object(filepaths=[obj.filepath],
                          workspace=self.workspace,
                          base_path=self.workspace,
                          original_name=obj.original_name,
                          file_format=file_format,
                          identifier=(obj.object_identifier_type,
                                      obj.object_identifier_value),
                          checksum=(obj.message_digest_algorithm,
                                    obj.message_digest))
            streams = read_json_streams(obj.filepath, self.workspace)
            if any(stream["stream_type"] == "image"
                   for stream in streams.values()):
                create_mix(obj.filepath, workspace=self.workspace,
                           base_path=self.workspace)
            if any(stream["stream_type"] == "video"
                   for stream in streams.values()):
                create_videomd(obj.filepath, workspace=self.workspace,
                               base_path=self.workspace)
            if any(stream["stream_type"] == "audio"
                   for stream in streams.values()):
                create_audiomd(obj.filepath, workspace=self.workspace,
                               base_path=self.workspace)
            if streams[0]["mimetype"] == "text/csv":
                create_addml(filename=obj.filepath,
                             workspace=self.workspace,
                             base_path=self.workspace,
                             header=True,
                             charset=streams[0]["charset"],
                             delim=streams[0]["delimiter"],
                             sep=streams[0]["separator"],
                             quot=streams[0]["quotechar"])
        print("Technical metadata created for %d file(s)."
              "" % (len(self.sip_meta.premis_objects)))

    def _create_provenance_metadata(self):
        """Create provenance matadata
        """
        print("Creating provenance metadata for %d event(s)."
              "" % (len(self.sip_meta.premis_events)))
        for event in self.sip_meta.events:
            for link in self.sip_meta.premis_linkings[
                    event.identifier].agent_links:
                agent = self.sip_meta.premis_agents[link["linking_agent"]]
                create_agent(
                    agent_name=agent.agent_name,
                    workspace=self.workspace,
                    agent_type=agent.agent_type,
                    agent_role=link["agent_role"],
                    agent_identifier=(agent.agent_identifier_type,
                                      agent.agent_identifier_value),
                    create_agent_file="siptools-tmp-%s-agent-file"
                                      "" % event.identifier)
            linking_objects = []
            for link in self.sip_meta.premis_linkings[
                    event.identifier].object_links:
                obj = self.sip_meta.premis_objects[link["linking_object"]]
                linking_objects.append(("target", obj.filepath))
            premis_event(
                event_type=event.event_type,
                event_datetime=event.event_datetime,
                workspace=self.workspace,
                base_path=self.workspace,
                linking_objects=linking_objects,
                event_detail=event.event_detail,
                event_outcome=event.event_outcome,
                event_outcome_detail=event.event_outcome_detail,
                create_agent_file="siptools-tmp-%s-agent-file"
                                  "" % event.identifier,
                add_object_links=True)
        print("Provenance metadata created for %d event(s)."
              "" % (len(self.sip_meta.premis_events)))

    def _import_descriptive_metadata(self):
        """Import descriptive metadata
        """
        print("Importing descriptive metadata.")
        found = False
        count = 0
        for filepath in self.sip_meta.descriptive_files(
                self.workspace, self.config):
            count += 1
            import_description(
                dmdsec_location=filepath,
                workspace=self.workspace,
                base_path=self.workspace,
                remove_root=self.sip_meta.desc_root_remove(self.config),
                dmd_agent=(os.path.basename(__file__), "software"))
            found = True
        if not found:
            raise IOError("Descriptive metadata file was not found!")
        print("Descriptive metadata imported from %d file(s)." % (count))

    def _compile_metadata(self):
        """
        Compile the generated metadata.

        Link the metadata files to file section and structural map and create
        METS document.
        """
        print("Compiling METS file.")
        compile_structmap(self.workspace)
        compile_mets(mets_profile="ch",
                     organization_name=self.config.name,
                     contractid=self.config.contract,
                     workspace=self.workspace,
                     base_path=self.workspace,
                     objid=self.sip_meta.objid,
                     clean=True)
        print("METS file created.")

    def _compile_package(self):
        """Sign SIP and create TAR file
        """
        print("Signing and packaging the SIP.")
        sign_mets(self.config.sign_key, self.workspace)
        tar_file = re.sub('[^0-9a-zA-Z]+', '_', self.sip_meta.objid)
        compress(
            dir_to_tar=self.workspace,
            tar_filename="%s.tar" % (tar_file),
            exclude=self.sip_meta.exclude_files(self.config))
        print("The SIP is signed and packaged to "
              "%s.tar" % (os.path.join(self.workspace, tar_file)))
        print("SIP signed and packaged.")

    def create_sip(self):
        """Create SIP in a TAR file
        """
        print("Cleaning possible old temporary files...")
        clean_temp_files(self.workspace)
        print("Packaging process started. Different steps create separate "
              "provenance metadata about the process in the SIP.")
        self._create_technical_metadata()
        self._create_provenance_metadata()
        self._import_descriptive_metadata()
        print("Compiling...")
        self._compile_metadata()
        self._compile_package()
        print("SIP creation finished.")


def compile_sip(workspace, conf_file=None):
    """SIP Compiler
    :workspace: Workspace path
    :conf_file: Configuration file path
    """
    if conf_file is None:
        conf_file = get_default_config_path()

    config = Config()
    config.configure(conf_file)

    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace=workspace,
                           config=config,
                           sip_meta=sip_meta)
    compiler.create_sip()


def clean_temp_files(workspace, file_endings=None, file_names=None):
    """
    Clean workspace from temporary files which match to given file endings
    or file names. If no endings nor names are given, default endings/names
    are used. This will clean the whole workspace from temporary files.

    :workspace: Workspace path
    :file_endings: Files matching tho the given endings will be removed.
    :file_names: Files matching to given names will be removed.
    """
    if file_endings is None and file_names is None:
        file_endings = (
            "-PREMIS%%3AOBJECT-amd.xml", "-ADDML-amd.xml",
            "-VideoMD-amd.xml", "-AudioMD-amd.xml", "-NISOIMG-amd.xml",
            "-PREMIS%%3AEVENT-amd.xml", "-PREMIS%%3AAGENT-amd.xml",
            "-AGENTS-amd.json", "-scraper.json", "-dmdsec.xml", ".tar")
        file_names = (
            "import-object-md-references.jsonl",
            "create-addml-md-references.jsonl",
            "create-audiomd-md-references.jsonl",
            "create-videomd-md-references.jsonl",
            "create-mix-md-references.jsonl",
            "premis-event-md-references.jsonl",
            "import-description-md-references.jsonl",
            "filesec.xml", "structmap.xml", "mets.xml", "signature.sig")
    if file_endings is None:
        file_endings = ()
    if file_names is None:
        file_names = ()

    for root, _, files in os.walk(workspace, topdown=False):
        for name in files:
            if name.endswith(file_endings) or name in file_names:
                os.remove(os.path.join(root, name))
