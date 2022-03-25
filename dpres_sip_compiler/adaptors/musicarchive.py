"""PREMIS metadata adaptor for Music Archive.
"""
import os
import glob
from io import open as io_open
import datetime
import re
import csv
import six
from dpres_sip_compiler.base_adaptor import (
    SipMetadata, PremisObject, PremisEvent, PremisAgent, PremisLinking)


def spaceless(string):
    """
    Strip string and change whitespaces to undercores.
    Consecutive whitespaces are changed to a single underscore.
    :string: String to be changed.
    :returns: Spaceless string
    """
    return re.sub(r"\s+", '_', string.strip())


def read_csv_file(filename):
    """
    Return all rows from CSV file as one dictionary per row.

    :filename: Filename to read
    :yields: CSV rows as dictionary

    """
    def _open_file(filename):
        """
        Open file in binary mode for Python 2,
        Otherwise in utf-8 text mode.

        :filename: File to open
        """
        if six.PY2:
            return io_open(filename, "rb")
        return io_open(filename, "rt", encoding="utf-8")

    with _open_file(filename) as infile:
        csvreader = csv.DictReader(infile, delimiter=',', quotechar='"')
        for row in csvreader:
            yield row


class SipMetadataMusicArchive(SipMetadata):
    """
    Music Archive specific PREMIS Metadata handler for a SIP to be compiled.
    """

    def populate(self, source_path, config):
        """
        Populate a CSV file to PREMIS dicts.
        The CSV file must be in the root directory of source path as it is
        not actual digital object in the content.

        :source_path: Source data path
        :config: Basic configuration
        """

        try:
            filename = glob.glob(
                os.path.join(
                    source_path, "*{}".format(config.csv_ending)))[0]
        except KeyError:
            raise IOError("CSV metadata file was not found!")

        for csv_row in read_csv_file(filename):
            self.add_premis_metadata(csv_row, source_path, config)

    def add_premis_metadata(self, csv_row, source_path, config):
        """Add premis metadata from single row of CSV metadata / dictionary

        :csv_row: CSV row as dict
        :source_path: Source data path
        :returns: None

        """
        p_object = PremisObjectMusicArchive(csv_row)
        if p_object.message_digest_algorithm.lower() == \
                config.used_checksum.lower():
            p_object.find_path(source_path)
            self.add_object(p_object)
        p_event = PremisEventMusicArchive(csv_row)
        self.add_event(p_event)
        self.premis_events[p_event.identifier].add_detail_info(
            csv_row)
        self.add_agent(PremisAgentMusicArchive(csv_row))
        self.add_linking(p_linking=PremisLinkingMusicArchive(csv_row),
                         object_id=csv_row["objekti-uuid"],
                         agent_id=csv_row["agent-id"],
                         agent_role=csv_row["agent-rooli"])
        if p_event.event_type == "information package creation" \
                and self.objid is None \
                and csv_row["sip-tunniste"] is not None:
            self.objid = spaceless(csv_row["sip-tunniste"])

    def descriptive_files(self, desc_path, config):
        """
        Iterator for descriptive metadata files.

        :desc_path: Path to descrptive metadata files
        :config: Additional needed configuration
        :returns: Descriptive metadata file
        """
        for filepath in os.listdir(desc_path):
            if filepath.endswith(config.meta_ending):
                yield os.path.join(desc_path, filepath)

    def desc_root_remove(self, config):
        """
        Resolve whether descriptive metadata root should be removed.
        :config: Additional needed configuration
        :returns: True/False
        """
        return config.desc_root_remove.lower() == "true"

    def exclude_files(self, config):
        """
        Exclude files from Submission Information Package.

        :config: Additional needed configuration
        :returns: Patterns for metadata files to be excluded.
        """
        return ("*%s" % config.meta_ending,
                "*%s" % config.csv_ending,
                ".[^/]*", "*/.[^/]*")  # Exclude all hidden files/directories


class PremisObjectMusicArchive(PremisObject):
    """
    Music Archive specific PREMIS Object handler.
    """

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        metadata = {
            "object_identifier_type": "UUID",
            "object_identifier_value": csv_row["objekti-uuid"],
            "original_name": csv_row["objekti-nimi"],
            "message_digest_algorithm": csv_row["tiiviste-tyyppi"],
            "message_digest": csv_row["tiiviste"]
        }
        super(PremisObjectMusicArchive, self).__init__(metadata)

    def find_path(self, source_path):
        """
        Find file path to object.
        :source_path: Source data path.
        :raises: IOError if digital object file was not found.
        """
        found = False
        for root, _, files in os.walk(source_path):
            if self.original_name in files:
                self.filepath = os.path.relpath(os.path.join(
                    root, self.original_name), source_path)
                found = True
                break

        if not found:
            raise IOError("Digital object %s was not found!"
                          "" % (self.original_name))


class PremisEventMusicArchive(PremisEvent):
    """
    Music Archive specific PREMIS Event handler.
    """
    DETAIL_KEYS = ["tiiviste", "tiiviste-tyyppi", "pon-korvattu-nimi",
                   "objekti-nimi", "sip-tunniste"]

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        self._detail_info = []
        metadata = {
            "event_identifier_type": "local",
            "event_identifier_value": csv_row["event-id"],
            "event_type": csv_row["event"],
            "event_outcome": csv_row["event-tulos"],
            "event_datetime": datetime.datetime.strptime(
                csv_row["event-aika"], "%Y-%m-%d %H:%M:%S"
                ).strftime("%Y-%m-%dT%H:%M:%S")
        }
        super(PremisEventMusicArchive, self).__init__(metadata)
        self.remove_metadata("event_detail")
        self.remove_metadata("event_outcome_detail")

    def add_detail_info(self, csv_row):
        """
        Add detailed information.

        This can not be in __init__() because if the event instance
        already exists, we just add more details to it.

        :csv_row: One row from a CSV file.
        """
        detail = {key: csv_row[key] for key in self.DETAIL_KEYS}
        if detail not in self._detail_info:
            self._detail_info.append(detail)

    @property
    def event_detail(self):
        """Event detail"""
        if self.event_type == "message digest calculation":
            return "Checksum calculation for digital objects."

        if self.event_type == "filename change":
            return "Filename change."

        if self.event_type == "information package creation":
            return "Creation of submission information package."

        raise NotImplementedError(
            "Not implemented event type '%s'." % (self.event_type))

    @property
    def event_outcome_detail(self):
        """Event outcome detail"""
        if self.event_outcome != "success":
            return "Event failed."

        if self.event_type == "message digest calculation":
            # The same algorithm exists in all elements of details
            out = "Checksum calculated with algorithm %s resulted the " \
                  "following checksums:" \
                  "" % self._detail_info[0]["tiiviste-tyyppi"]
            for info in self._detail_info:
                out = "%s\n%s: %s" % (out, info["objekti-nimi"],
                                      info["tiiviste"])
            return out

        if self.event_type == "filename change":
            # There's only one element in details
            return "Filename changed.\nOld filename: %s\nNew filename: %s\n" \
                   "" % (self._detail_info[0]["pon-korvattu-nimi"],
                         self._detail_info[0]["objekti-nimi"])

        if self.event_type == "information package creation":
            # There's only one element in details
            return "Submission information package created as: " \
                   "%s" % spaceless(self._detail_info[0]["sip-tunniste"])

        raise NotImplementedError(
            "Not implemented event type '%s'." % (self.event_type))


class PremisAgentMusicArchive(PremisAgent):
    """
    Music Archive specific PREMIS Agent handler.
    """

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        metadata = {
            "agent_identifier_type": "local",
            "agent_identifier_value": csv_row["agent-id"],
            "agent_name": csv_row["agent-nimi"],
            "agent_type": csv_row["agent-tyyppi"],
        }
        super(PremisAgentMusicArchive, self).__init__(metadata)


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

    def add_object_link(self, identifier):
        """
        Add object to linking. Skip object adding if event type is
        'information package creation'.
        :identifier: PREMIS Object identifier
        """
        if self._event_type == "information package creation":
            return
        super(PremisLinkingMusicArchive, self).add_object_link(identifier)
