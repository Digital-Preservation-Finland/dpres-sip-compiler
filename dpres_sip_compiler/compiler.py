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
from dpres_sip_compiler.config import Config
from dpres_sip_compiler.selector import select


class SipCompiler(object):
    """Compiler to create SIPs
    """

    def __init__(self, workspace, config, sip_meta):
        """Initialize compiler.

        :workspace: Workspace path
        :config: Basic cnofiguration
        :sip_meta: PREMIS metadata objects for the SIP to be compiled.
        """
        self.workspace = workspace
        self.config = config
        self.sip_meta = sip_meta

    def _technical_metadata(self):
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

    def _provenance_metadata(self):
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

    def _descriptive_metadata(self):
        """Create descriptive metadata
        """
        found = False
        count = 0
        print("Importing descriptive metadata.")
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

    def create_mets(self):
        """Create full METS document
        """
        print("Packaging process started. Different steps create separate "
              "provenance metadata about the process in the SIP.")
        objid = self.sip_meta.objid
        self._technical_metadata()
        self._provenance_metadata()
        self._descriptive_metadata()
        print("Compiling...")
        compile_structmap(self.workspace)
        compile_mets(mets_profile="ch",
                     organization_name=self.config.name,
                     contractid=self.config.contract,
                     workspace=self.workspace,
                     base_path=self.workspace,
                     objid=objid,
                     clean=True)
        sign_mets(self.config.sign_key, self.workspace)
        tar_file = re.sub('[^0-9a-zA-Z]+', '_', objid)
        compress(
            dir_to_tar=self.workspace,
            tar_filename="%s.tar" % (tar_file),
            exclude=self.sip_meta.exclude_files(self.config))
        print("Compiling done. The SIP is signed and packaged to "
              "%s.tar" % (os.path.join(self.workspace, tar_file)))


def compile_sip(conf_file, workspace):
    """SIP Compiler
    :conf_file: Configuration file path
    :workspace: Workspace path
    """
    config = Config()
    config.configure(conf_file)

    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace=workspace,
                           config=config,
                           sip_meta=sip_meta)
    compiler.create_mets()


def clean_workspace(workspace):
    """Clean workspace from temporary files.
    This is currently needed if the packaging gets iterrupted.
    :workspace: Workspace path
    """
    for root, _, files in os.walk(workspace, topdown=False):
        for name in files:
            if (name.endswith(("-amd.xml", "dmdsec.xml", "structmap.xml",
                               "filesec.xml", "rightsmd.xml",
                               "md-references.jsonl",
                               "-scraper.json", "-amd.json",
                               "mets.xml", "signature.sig", ".tar"))):
                os.remove(os.path.join(root, name))
    print("Temporary files were cleaned from workspace.")
