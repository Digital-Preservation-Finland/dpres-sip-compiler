"""
"""
import os
import csv
from dpres_sip_compiler.base_adaptor import (
    SipMeta, PremisObject, PremisEvent, PremisAgent, PremisLinking)

class SipMetaMusicArchive(SipMeta):
    """
    """
    def populate(self, workspace, config):
        csvfile = None
        for filepath in os.listdir(workspace):
            if filepath.endswith("%s.csv" % config.meta_ending):
                csvfile = os.path.join(workspace, filepath)
                break
        if not csvfile:
            raise IOError("CSV metadata file was not found!")
        with open(csvfile) as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for csv_row in csvreader:
                self._add_object(csv_row=csv_row, config=config,
                                 workspace=workspace)
                self._add_event(csv_row)
                self._add_agent(csv_row)
                self._add_linking(csv_row)

    def _add_object(self, csv_row, config, workspace):
        _object = PremisObjectMusicArchive(csv_row)
        if _object.message_digest_algorithm.lower() == \
                config.used_checksum.lower():
            _object.find_path(workspace)
            self.premis_objects[csv_row["objekti-uuid"]] = _object

    def _add_event(self, csv_row):
        self.premis_events[csv_row["event-id"]] = PremisEventMusicArchive(
            csv_row)

    def _add_agent(self, csv_row):
        self.premis_agents[csv_row["agent-id"]] = PremisAgentMusicArchive(
            csv_row)

    def _add_linking(self, csv_row):
        _linking = PremisLinkingMusicArchive(csv_row)
        if not _linking.identifier in self.premis_linkings:
            self.premis_linkings[_linking.identifier] = _linking
        self.premis_linkings[_linking.identifier].add_object(csv_row=csv_row)
        self.premis_linkings[_linking.identifier].add_agent(csv_row=csv_row)


class PremisObjectMusicArchive(PremisObject):
    """
    """
    CSV_KEYS = ["objekti-uuid", "objekti-nimi", "tiiviste-tyyppi", "tiiviste"]

    def __init__(self, csv_row):
        """
        """
        super(PremisObjectMusicArchive, self).__init__()
        self._csv_object = {key: csv_row[key] for key in self.CSV_KEYS}


    def find_path(self, workspace):
        """
        """
        found = False
        for root, _, files in os.walk(workspace):
            if self._csv_object["objekti-nimi"] in files:
                self.filepath = os.path.relpath(os.path.join(
                    root, self._csv_object["objekti-nimi"]), workspace)
                found = True
                break

        if not found:
            raise IOError("Digital object %s was not found!"
                          "" % self._csv_object["objekti-nimi"])

    @property
    def object_identifier_type(self):
        return "UUID"

    @property
    def object_identifier_value(self):
        return self._csv_object["objekti-uuid"]

    @property
    def original_name(self):
        return self._csv_object["objekti-nimi"]

    @property
    def message_digest_algorithm(self):
        return self._csv_object["tiiviste-tyyppi"]

    @property
    def message_digest(self):
        return self._csv_object["tiiviste"]


class PremisEventMusicArchive(PremisEvent):

    CSV_KEYS = ["event-id", "event", "event-aika", "event-tulos"]

    def __init__(self, csv_row):
        """
        """
        self._csv_event = {key: csv_row[key] for key in self.CSV_KEYS}

    @property
    def event_identifier_type(self):
        return "local"

    @property
    def event_identifier_value(self):
        return self._csv_event["event-id"]

    @property
    def event_type(self):
        return self._csv_event["event"]

    @property
    def event_datetime(self):
        return self._csv_event["event-aika"]

    @property
    def event_outcome(self):
        return self._csv_event["event-tulos"]


class PremisAgentMusicArchive(PremisAgent):

    CSV_KEYS = ["agent-id", "agent-nimi", "agent-tyyppi"]

    def __init__(self, csv_row):
        """
        """
        self._csv_agent = {key: csv_row[key] for key in self.CSV_KEYS}

    @property
    def agent_identifier_type(self):
        return "local"

    @property
    def agent_identifier_value(self):
        return self._csv_agent["agent-id"]

    @property
    def agent_name(self):
        return self._csv_agent["agent-nimi"]

    @property
    def agent_type(self):
        return self._csv_agent["agent-tyyppi"]


class PremisLinkingMusicArchive(PremisLinking):

    def __init__(self, csv_row):
        """
        """
        super(PremisLinkingMusicArchive, self).__init__(csv_row=csv_row)
        self.identifier = csv_row["event-id"]

    def add_object(self, csv_row):
        if csv_row["event"] == "information package creation":
            return
        found = False
        for obj in self.objects:
            if csv_row["objekti-uuid"] in obj["linking_object"]:
                found = True
                break
        if not found:
            self.objects.append({"linking_object": csv_row["objekti-uuid"]})

    def add_agent(self, csv_row):
        found = False
        for agent in self.agents:
            if csv_row["agent-id"] in agent["linking_agent"]:
                found = True
                break
        if not found:
            self.agents.append({"linking_agent": csv_row["agent-id"],
                                "agent_role": csv_row["agent-rooli"]})
