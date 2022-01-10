"""PREMIS metadata adaptor for Music Archive.
"""
import os
import csv
from dpres_sip_compiler.base_adaptor import (
    SipPremis, PremisObject, PremisEvent, PremisAgent, PremisLinking)

class SipPremisMusicArchive(SipPremis):
    """
    Music Archive specific PREMIS Metadata handler for a SIP to be compiled.
    """

    def populate(self, workspace, config):
        """
        Populate a CSV file to PREMIS dicts.

        :workspace: Data workspace
        :config: Basic configuration
        """
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
    Music Archive specific PREMIS Object handler.
    """
    CSV_KEYS = ["objekti-uuid", "objekti-nimi", "tiiviste-tyyppi", "tiiviste"]

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        super(PremisObjectMusicArchive, self).__init__()
        self._csv_object = {key: csv_row[key] for key in self.CSV_KEYS}


    def find_path(self, workspace):
        """
        Find file path to object.
        :workspace: Workspace path.
        :raises: IOError if digital object file was not found.
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
        """All objectIdentifierTypes are UUIDs"""
        return "UUID"

    @property
    def object_identifier_value(self):
        """Object ID value from a CSV file"""
        return self._csv_object["objekti-uuid"]

    @property
    def original_name(self):
        """Object orginal name from a CSV file"""
        return self._csv_object["objekti-nimi"]

    @property
    def message_digest_algorithm(self):
        """Message digest algorithm from a CSV file"""
        return self._csv_object["tiiviste-tyyppi"]

    @property
    def message_digest(self):
        """Message digest from a CSV file"""
        return self._csv_object["tiiviste"]


class PremisEventMusicArchive(PremisEvent):
    """
    Music Archive specific PREMIS Event handler.
    """

    CSV_KEYS = ["event-id", "event", "event-aika", "event-tulos"]

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        self._csv_event = {key: csv_row[key] for key in self.CSV_KEYS}

    @property
    def event_identifier_type(self):
        """All event IDs are local"""
        return "local"

    @property
    def event_identifier_value(self):
        """Event ID value from a CSV file"""
        return self._csv_event["event-id"]

    @property
    def event_type(self):
        """Event type from a CSV file"""
        return self._csv_event["event"]

    @property
    def event_datetime(self):
        """Event timestamp from a CSV file"""
        return self._csv_event["event-aika"]

    @property
    def event_outcome(self):
        """Event outcome from a CSV file"""
        return self._csv_event["event-tulos"]


class PremisAgentMusicArchive(PremisAgent):
    """
    Music Archive specific PREMIS Agent handler.
    """

    CSV_KEYS = ["agent-id", "agent-nimi", "agent-tyyppi"]

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        self._csv_agent = {key: csv_row[key] for key in self.CSV_KEYS}

    @property
    def agent_identifier_type(self):
        """All agent IDs are local"""
        return "local"

    @property
    def agent_identifier_value(self):
        """Agent ID value from a CSV file"""
        return self._csv_agent["agent-id"]

    @property
    def agent_name(self):
        """Agent name from a CSV file"""
        return self._csv_agent["agent-nimi"]

    @property
    def agent_type(self):
        """Agent type from a CSV file"""
        return self._csv_agent["agent-tyyppi"]


class PremisLinkingMusicArchive(PremisLinking):
    """
    Music Archive specific PREMIS Linking handler.
    """

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        super(PremisLinkingMusicArchive, self).__init__()
        self._event_type = csv_row["event"]
        self.identifier = csv_row["event-id"]

    def add_object(self, identifier):
        """
        Add object to linking. Skip object adding if event type is
        'information package creation'
        :identifier: PREMIS Object identifier
        """
        if self._event_type == "information package creation":
            return
        super(PremisLinkingMusicArchive, self).add_object(identifier)
