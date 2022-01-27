"""Compile SIP based on a given metadata source.

Adaptors for different types of sources may be added.
"""
import sys
import os
import click
from siptools.scripts.import_object import import_object
from siptools.scripts.create_mix import create_mix
from siptools.scripts.create_videomd import create_videomd
from siptools.scripts.create_audiomd import create_audiomd
from siptools.scripts.import_description import import_description
from siptools.scripts.premis_event import premis_event
from siptools.scripts.create_agent import create_agent
from siptools.scripts.compile_structmap import compile_structmap
from siptools.scripts.compile_mets import compile_mets
from siptools.scripts.sign_mets import sign_mets
from siptools.scripts.compress import compress
from siptools.utils import read_json_streams
from dpres_sip_compiler.config import Config
from dpres_sip_compiler.adaptors.musicarchive import \
    SipMetadataMusicArchive

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
        for obj in self.sip_meta.objects:
            import_object(filepaths=[obj.filepath],
                          workspace=self.workspace,
                          base_path=self.workspace,
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

    def _provenance_metadata(self):
        """Create provenance matadata
        """
        for event in self.sip_meta.events:
            for link in self.sip_meta.premis_linkings[
                    event.identifier].agents:
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
                    event.identifier].objects:
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

    def _descriptive_metadata(self):
        """Create descriptive metadata
        """
        found = False
        for filepath in os.listdir(self.workspace):
            if filepath.endswith(self.config.meta_ending):
                import_description(
                    dmdsec_location=os.path.join(self.workspace, filepath),
                    workspace=self.workspace,
                    base_path=self.workspace,
                    dmd_agent=(os.path.basename(__file__), "software"))
                found = True
        if not found:
            raise IOError("Descriptive metadata file was not found!")

    def create_mets(self):
        """Create full METS document
        """
        objid = self.sip_meta.objid
        self._technical_metadata()
        self._provenance_metadata()
        self._descriptive_metadata()
        compile_structmap(self.workspace)
        compile_mets(mets_profile="ch",
                     organization_name=self.config.name,
                     contractid=self.config.contract,
                     workspace=self.workspace,
                     base_path=self.workspace,
                     objid=objid,
                     clean=True)
        sign_mets(self.config.sign_key, self.workspace)
        # TODO: add exclude option to compress
        # compress(self.workspace, os.path.join(self.workspace, objid+".tar"),
        #          exclude="*%s" % self.config.meta_ending)


def compile_sip(conf_file, workspace):
    """SIP Compiler
    :conf_file: Configuration file path
    :workspace: Workspace path
    """
    config = Config()
    config.configure(conf_file)

    sip_meta = None
    
    if config.adaptor == "musicarchive":
        sip_meta = SipMetadataMusicArchive()
        sip_meta.populate(workspace, config)
    else:
        raise NotImplementedError("Unsupported configuration!")

    compiler = SipCompiler(workspace=workspace,
                           config=config,
                           sip_meta=sip_meta)
    compiler.create_mets()


@click.command()
@click.argument('configure', type=click.Path(exists=True))
@click.argument('workspace', type=click.Path(exists=True))
def main(configure, workspace):
    """SIP Compiler.
    :configure: Configuration path
    :workspace: Workspace path
    """
    compile_sip(configure, workspace)
    return 0


if __name__ == '__main__':
    RETVAL = main()  # pylint: disable=no-value-for-parameter
    sys.exit(RETVAL)
