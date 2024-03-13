"""
Compile SIP based on a given metadata source.
Adaptors for different types of sources may be added.
"""

import os
import subprocess
import re
import datetime
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
from siptools.utils import read_json_streams, fsencode_path
from dpres_sip_compiler.base_adaptor import build_sip_metadata
from dpres_sip_compiler.adaptor_list import ADAPTOR_DICT
from dpres_sip_compiler.config import (Config, get_default_config_path,
                                       get_default_temp_path)


# pylint: disable=too-few-public-methods
class SipCompiler:
    """Compiler to create SIPs
    """

    # pylint: disable=too-many-arguments
    def __init__(self, source_path, temp_path, config, sip_meta,
                 tar_file=None, validation=True):
        """Initialize compiler.

        :source_path Source path of the files to be packaged
        :temp_path: Path for temporary files
        :config: Basic configuration
        :sip_meta: PREMIS metadata objects for the SIP to be compiled.
        :tar_file: Target TAR file for the SIP
        :validation: True to validate files during packaging, False otherwise
        """
        self.source_path = source_path
        self.temp_path = temp_path
        self.config = config
        self.sip_meta = sip_meta
        self.tar_file = tar_file
        self.validation = validation

    def _create_technical_metadata(self):
        """Create technical metadata
        """
        print("Creating technical metadata for %d file(s)."
              "" % (len(self.sip_meta.premis_objects)))
        event_datetime = datetime.datetime.now().isoformat()
        for obj in self.sip_meta.objects:
            file_format = (obj.format_name, obj.format_version)
            if obj.format_name is None:
                file_format = ()
            import_object(filepaths=[obj.filepath],
                          workspace=self.temp_path,
                          base_path=self.source_path,
                          original_name=obj.original_name,
                          file_format=file_format,
                          identifier=(obj.object_identifier_type,
                                      obj.object_identifier_value),
                          checksum=(obj.message_digest_algorithm,
                                    obj.message_digest),
                          event_datetime=event_datetime,
                          event_target=".",
                          skip_wellformed_check=not self.validation)
            streams = read_json_streams(obj.filepath, self.temp_path)
            if any(stream["stream_type"] == "image"
                   for stream in streams.values()):
                create_mix(obj.filepath, workspace=self.temp_path,
                           base_path=self.source_path)
            if any(stream["stream_type"] == "video"
                   for stream in streams.values()):
                create_videomd(obj.filepath, workspace=self.temp_path,
                               base_path=self.source_path)
            if any(stream["stream_type"] == "audio"
                   for stream in streams.values()):
                create_audiomd(obj.filepath, workspace=self.temp_path,
                               base_path=self.source_path)
            if streams[0]["mimetype"] == "text/csv":
                create_addml(filename=obj.filepath,
                             workspace=self.temp_path,
                             base_path=self.source_path,
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
                    workspace=self.temp_path,
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
                obj_role = obj.__getattr__("object_role")
                if obj_role in ["source", "outcome"]:
                    linking_objects.append((obj_role, obj.filepath))
                else:
                    linking_objects.append(("target", obj.filepath))
            premis_event(
                event_type=event.event_type,
                event_datetime=event.event_datetime,
                workspace=self.temp_path,
                base_path=self.source_path,
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
                self.source_path, self.config):
            count += 1
            import_description(
                dmdsec_location=filepath,
                workspace=self.temp_path,
                base_path=self.source_path,
                remove_root=self.sip_meta.desc_root_remove(self.config),
                dmd_agent=(os.path.basename(__file__), "software"))
            found = True
        if not found:
            raise OSError("Descriptive metadata file was not found!")
        print("Descriptive metadata imported from %d file(s)." % (count))

    def _compile_metadata(self):
        """
        Compile the generated metadata.

        Link the metadata files to file section and structural map and create
        METS document.
        """
        print("Compiling METS file.")
        compile_structmap(self.temp_path)
        compile_mets(mets_profile="ch",
                     organization_name=self.config.name,
                     contractid=self.config.contract,
                     workspace=self.temp_path,
                     base_path=self.source_path,
                     objid=self.sip_meta.objid,
                     clean=True)
        print("METS file created.")

    def _post_adaptor_tasks(self):
        """Additional tasks to workspace.
        """
        self.sip_meta.post_tasks(self.temp_path, self.source_path)

    def _compile_package(self):
        """Sign SIP and create TAR file
        """
        print("Signing and packaging the SIP.")
        sign_mets(self.config.sign_key, self.temp_path)

        if self.tar_file is None:
            self.tar_file = os.path.join(
                os.getcwd(), "%s.tar" % re.sub('[^0-9a-zA-Z-]+',
                                               '_',
                                               self.sip_meta.objid))

        if not os.path.exists(os.path.dirname(self.tar_file)):
            os.makedirs(os.path.dirname(self.tar_file))

        returncode = compress(
            dir_to_tar=self.source_path,
            tar_filename=os.path.abspath(self.tar_file),
            exclude=self.sip_meta.exclude_files(self.config))
        if returncode != 0:
            raise ValueError("TAR packaging error. Return code was: "
                             "%s" % str(returncode))

    # Popen does not support with in Python2
    # pylint: disable=consider-using-with
    def _append_tar(self):
        """Append METS and signature to TAR file.
        """
        if os.path.normpath(self.temp_path) == os.path.normpath(
                self.source_path):
            return
        print("Append METS and signature to TAR file.")
        command = ["tar", "-rvvf", fsencode_path(self.tar_file), "./mets.xml",
                   "./signature.sig"]
        proc = subprocess.Popen(
            command, cwd=self.temp_path,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, close_fds=True
        )

        proc.communicate()
        if proc.returncode != 0:
            raise ValueError("TAR packaging error. Return code was: "
                             "%s" % str(proc.returncode))

    def create_sip(self, temp_path_created=False):
        """Create SIP in a TAR file
        :temp_path_created: True, if directory for temporary files was created
                            during the process, False otherwise
        """
        print("Cleaning possible old temporary files.")
        clean_temp_files(self.temp_path)
        print("Packaging process started. Different steps create separate "
              "provenance metadata about the process in the SIP.")
        self._create_technical_metadata()
        self._create_provenance_metadata()
        self._import_descriptive_metadata()
        print("Compiling...")
        self._compile_metadata()
        print("Running additional tasks...")
        self._post_adaptor_tasks()
        print("Compiling...")
        self._compile_package()
        self._append_tar()
        print("Cleaning temporary files.")
        clean_temp_files(self.temp_path, delete_path=temp_path_created)
        print("Compilation finished. The SIP is signed and packaged to: "
              "%s" % self.tar_file)


def compile_sip(source_path, tar_file=None, temp_path=None, conf_file=None,
                validation=True):
    """SIP Compiler
    :source_path: Source path of files to be packaged
    :tar_file: Target TAR file for the SIP
    :temp_path: Path of temporary files
    :conf_file: Configuration file path
    :validation: True to validate files during packaging, False otherwise
    """
    if conf_file is None:
        conf_file = get_default_config_path()
    if temp_path is None:
        temp_path = get_default_temp_path()

    temp_path_created = False
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
        temp_path_created = True

    config = Config()
    config.configure(conf_file)

    sip_meta = build_sip_metadata(ADAPTOR_DICT, source_path, config)
    compiler = SipCompiler(source_path=source_path,
                           tar_file=tar_file,
                           temp_path=temp_path,
                           config=config,
                           sip_meta=sip_meta,
                           validation=validation)
    compiler.create_sip(temp_path_created)


def clean_temp_files(temp_path, file_endings=None, file_names=None,
                     delete_path=False):
    """
    Clean directory from temporary files which match to given file endings
    or file names. If no endings nor names are given, default endings/names
    are used. This will clean the whole directory from temporary files.

    :temp_path: Directory containing temporary files
    :file_endings: Files matching tho the given endings will be removed.
    :file_names: Files matching to given names will be removed.
    :delete_path: True to remove directory of temporary files.
                  Removed only, if it is empty after cleaning.
    """
    if file_endings is None and file_names is None:
        file_endings = (
            "-PREMIS%%3AOBJECT-amd.xml", "-ADDML-amd.xml",
            "-VideoMD-amd.xml", "-AudioMD-amd.xml", "-NISOIMG-amd.xml",
            "-PREMIS%%3AEVENT-amd.xml", "-PREMIS%%3AAGENT-amd.xml",
            "-AGENTS-amd.json", "-scraper.json", "-dmdsec.xml")
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

    for root, _, files in os.walk(temp_path, topdown=False):
        for name in files:
            if name.endswith(file_endings) or name in file_names:
                os.remove(os.path.join(root, name))

    if delete_path:
        try:
            os.rmdir(temp_path)
        except OSError:
            print("NOTE: Directory %s was not removed, because it includes "
                  "files." % temp_path)
