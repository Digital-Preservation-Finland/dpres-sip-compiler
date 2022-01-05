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
                p_object = PremisObjectMusicArchive(csv_row)
                if p_object.message_digest_algorithm.lower() == \
                        config.used_checksum.lower():
                    p_object.find_path(workspace)
                    self.add_object(p_object)
                self.add_event(PremisEventMusicArchive(csv_row))
                self.add_agent(PremisAgentMusicArchive(csv_row))
                self.add_linking(p_linking=PremisLinkingMusicArchive(csv_row),
                                 object_id=csv_row["objekti-uuid"],
                                 agent_id=csv_row["agent-id"],
                                 agent_role=csv_row["agent-rooli"])


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
        self._event_type = csv_row["event"]
        self.identifier = csv_row["event-id"]

    def add_object(self, identifier):
        if self._event_type == "information package creation":
            return
        super(PremisLinkingMusicArchive, self).add_object(identifier)
