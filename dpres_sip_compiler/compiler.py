"""
"""
import sys
import os
import configparser
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
from dpres_sip_compiler.csv_reader import read_csv


class SipCompiler(object):
    """Compiler to create SIPs
    """

    def __init__(self, workspace, script_config, objects, events, event_rels):
        """Initialize compiler
        """
        self.workspace = workspace
        self.config = script_config
        self.objects = objects
        self.events = events
        self.event_rels = event_rels

    def _find_paths(self):
        """Find paths of given file names, which are unique inside data set
        """
        found = False
        for obj in self.objects:
            found = False
            for root, _, files in os.walk(self.workspace):
                if obj["name"] in files:
                    relpath = os.path.relpath(os.path.join(
                        root, obj["name"]), self.workspace)
                    obj["path"] = relpath
                    for key in self.event_rels:
                        if obj["id"] in self.event_rels[key]["objects"]:
                            self.event_rels[key]["paths"].append(relpath)
                    found = True
                    break

            if not found:
                raise IOError("Digital object %s was not found!"
                              "" % obj["name"])
        if not found:
            raise IOError("No digital objects.")
        # TODO: Does not check extra files

    def _technical_metadata(self):
        """Create technical metadata
        """
        for obj in self.objects:
            import_object(filepaths=[obj["path"]],
                          workspace=self.workspace,
                          base_path=self.workspace,
                          identifier=(self.config["object_idtype"],
                                      obj["id"]),
                          checksum=(self.config["used_checksum"],
                                    obj["sum"]))
            streams = read_json_streams(obj["path"], self.workspace)
            if any(stream["stream_type"] == "image"
                   for stream in streams.values()):
                create_mix(obj["path"], workspace=self.workspace,
                           base_path=self.workspace)
            if any(stream["stream_type"] == "video"
                   for stream in streams.values()):
                create_videomd(obj["path"], workspace=self.workspace,
                               base_path=self.workspace)
            if any(stream["stream_type"] == "audio"
                   for stream in streams.values()):
                create_audiomd(obj["path"], workspace=self.workspace,
                               base_path=self.workspace)

    def _provenance_metadata(self):
        """Create provenance matadata
        """
        for event in self.events:
            for agent in self.event_rels[event["id"]]["agents"]:
                create_agent(
                    agent_name=agent["name"],
                    workspace=self.workspace,
                    agent_type=agent["type"],
                    agent_role=agent["role"],
                    agent_identifier=(self.config["agent_idtype"],
                                      agent["id"]),
                    create_agent_file="siptools-tmp-agent-file")
            linking_objects = []
            for obj_path in self.event_rels[event["id"]]["paths"]:
                linking_objects.append(("target", obj_path))
            detail = "FOO DETAIL"  # TODO: Detailed info
            outcome_detail = "FOO OUTCOME DETAIL"  # TODO: Detailed info
            premis_event(
                event_type=event["type"],
                event_datetime=event["datetime"],
                workspace=self.workspace,
                base_path=self.workspace,
                linking_objects=linking_objects,
                event_detail=detail,
                event_outcome=event["outcome"],
                event_outcome_detail=outcome_detail,
                create_agent_file="siptools-tmp-agent-file",
                add_object_links=True)

    def _descriptive_metadata(self):
        """Create descriptive metadata
        """
        found = False
        for filepath in os.listdir(self.workspace):
            if filepath.endswith("%s.xml" % self.config["meta_ending"]):
                import_description(
                    dmdsec_location=os.path.join(self.workspace, filepath),
                    workspace=self.workspace,
                    base_path=self.workspace,
                    dmd_agent=(os.path.basename(__file__), "software"))
                found = True
        if not found:
            raise IOError("Descriptive metadata file was not found!")

    def create_mets(self, org_info):
        """Create full METS document
        """
        objid = os.path.basename(os.path.relpath(self.workspace))
        self._find_paths()
        self._technical_metadata()
        self._provenance_metadata()
        self._descriptive_metadata()
        compile_structmap(self.workspace)
        compile_mets(mets_profile="ch",
                     organization_name=org_info["name"],
                     contractid=org_info["contract"],
                     workspace=self.workspace,
                     base_path=self.workspace,
                     objid=objid,
                     clean=True)
        sign_mets(org_info["sign_key"], self.workspace)
        # TODO: add exclude option to compress
        # compress(self.workspace, os.path.join(self.workspace, objid+".tar"),
        #          exclude="*%s.*" % self.config["meta_ending"])


def compile_sip(conf_file, workspace):
    """SIP Compiler
    """
    config = configparser.ConfigParser()
    config.read(conf_file)
    (objects, events, event_rels) = read_csv(workspace, config)
    compiler = SipCompiler(workspace=workspace,
                           script_config=config["script"],
                           objects=objects,
                           events=events,
                           event_rels=event_rels)
    compiler.create_mets(config["organization"])


@click.command()
@click.argument('configure', type=click.Path(exists=True))
@click.argument('workspace', type=click.Path(exists=True))
def main(configure, workspace):
    """SIP Compiler
    """
    compile_sip(configure, workspace)
    return 0


if __name__ == '__main__':
    RETVAL = main()  # pylint: disable=no-value-for-parameter
    sys.exit(RETVAL)
