"""PREMIS metadata adaptor for Music Archive.
"""
import os
import glob
from io import open as io_open
import datetime
import csv
import premis
import mets as metslib
from file_scraper.scraper import Scraper
from xml_helpers import utils as xml_utils
from dpres_sip_compiler.base_adaptor import (
    SipMetadata, PremisObject, PremisEvent, PremisAgent, PremisLinking)


def read_csv_file(filename):
    """
    Return all rows from CSV file as one dictionary per row.

    :filename: Filename to read
    :yields: CSV rows as dictionary

    """
    def _open_file(filename):
        """
        Open file in utf-8 text mode.

        :filename: File to open
        """
        return io_open(filename, "rt", encoding="utf-8")

    with _open_file(filename) as infile:
        csvreader = csv.DictReader(infile, delimiter=',', quotechar='"')
        yield from csvreader


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
                    source_path, f"*{config.csv_ending}"))[0]
        except KeyError:
            raise OSError("CSV metadata file was not found!")

        self.objid = os.path.split(filename)[1].replace(config.csv_ending, "")

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
                config.used_checksum.lower() and p_object.digest_valid:
            p_object.find_path(source_path)
            self.add_object(p_object)
        p_event = PremisEventMusicArchive(csv_row)
        self.add_event(p_event)
        self.premis_events[p_event.identifier].add_detail_info(
            csv_row)
        self.add_agent(PremisAgentMusicArchive(csv_row))
        self.add_linking(p_linking=PremisLinkingMusicArchive(csv_row),
                         object_id=csv_row["objekti-uuid"],
                         agent_id="agent-"+csv_row["agent-id"],
                         agent_role=csv_row["agent-rooli"])

    def descriptive_files(self, desc_path, config):
        """
        Iterator for descriptive metadata files.

        :desc_path: Path to descrptive metadata files
        :config: Additional needed configuration
        :returns: Descriptive metadata file
        """
        for filepath in os.listdir(desc_path):
            if filepath.endswith(config.meta_ending) and \
                    not filepath.startswith("."):
                yield os.path.join(desc_path, filepath)

    def desc_root_remove(self, config):
        """
        Resolve whether descriptive metadata root should be removed.
        :config: Additional needed configuration
        :returns: True/False
        """
        return config.desc_root_remove.lower() == "true"

    @staticmethod
    def exclude_files(config):
        """
        Exclude files from Submission Information Package.

        :config: Additional needed configuration
        :returns: Patterns for metadata files to be excluded.
        """
        return ("*%s" % config.meta_ending,
                "*%s" % config.csv_ending,
                ".[!/]*", "*/.[!/]*")  # Exclude all hidden files/directories

    def post_tasks(self, workspace, source_path):

        """
        Post tasks to workspace not supported by dpres-siptools.

        Open and write METS file here, because in this adaptor the possible
        future tasks are assumend to be related to METS.

        :workspace: Workspace path
        :source_path: Source path of files to be packaged
        """
        mets_file = os.path.join(workspace, "mets.xml")
        mets = xml_utils.readfile(mets_file)

        # Post tasks for the METS file
        mets = self._append_alternative_ids(mets)
        mets = handle_html_files(mets, source_path)

        with open(mets_file, 'wb+') as outfile:
            outfile.write(xml_utils.serialize(mets.getroot()))

    def _append_alternative_ids(self, mets):
        """
        Add additional PREMIS object identifiers to METS.

        :mets: METS XML root
        """
        for xml_object in premis.iter_objects(mets):
            if premis.parse_object_type(xml_object) != "premis:file":
                continue

            # Check if there already are multiple IDs in the object
            if len(xml_object.xpath(
                    "./premis:objectIdentifier",
                    namespaces={'premis': 'info:lc/xmlns/premis-v2'})) > 1:
                continue

            (_, id_value) = premis.parse_identifier_type_value(xml_object)
            id_value = id_value.strip()
            p_object = self.premis_objects[id_value]
            xml_id = premis.identifier(p_object.alt_identifier_type,
                                       p_object.alt_identifier_value)
            xml_object.insert(1, xml_id)

        return mets

def handle_html_files(mets, source_path):
    """
    Run validation on all HTML files. If the HTML file is broken, change
    the formatName to TEXT and remove formatVersion in the METS file.

    :mets: METS XML root
    :source_path: Source path of files to be packaged
    """
    format_elems = mets.xpath(
        ".//premis:format[contains(.//premis:formatName, 'text/html')]",
        namespaces={'premis': 'info:lc/xmlns/premis-v2'})
    if not format_elems:
        return mets

    for format_elem in format_elems:
        techmd_id = format_elem.xpath(
            "ancestor::mets:techMD/@ID",
            namespaces={
                'mets': 'http://www.loc.gov/METS/'})[0]
        file_path = find_path_by_techmd_id(mets, techmd_id)

        scraper = Scraper(os.path.join(source_path, file_path))
        scraper.scrape(check_wellformed=True)
        well_formed = scraper.well_formed

        if well_formed is False:
            premis.modify_element_value(
                format_elem, "formatName", "text/plain; alt-format=text/html")
            format_version_element = format_elem.xpath(
                ".//premis:formatVersion",
                namespaces={
                    'premis': 'info:lc/xmlns/premis-v2'})

            if format_version_element:
                format_version_element[0].getparent().remove(
                    format_version_element[0])

    return mets


def find_path_by_techmd_id(mets, techmd_id):
    """
    Find the file path that matches the given METS TechMD ID.
    :mets: METS XML root
    :techmd_id: TechMD element's ID value
    """
    for file_elem in metslib.parse_files(mets):
        admid_list = metslib.parse_admid(file_elem)
        if techmd_id in admid_list:
            flocat_elem = metslib.parse_flocats(file_elem)[0]
            href = metslib.parse_href(flocat_elem)
            file_path = href[len('file://'):]

    return file_path


class PremisObjectMusicArchive(PremisObject):
    """
    Music Archive specific PREMIS Object handler.
    """

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """

        # We may have CSV files without the digest status information.
        # In such case, the message digest is always valid.
        self.digest_valid = \
            True if csv_row.get("tiiviste-status", "1") == "1" else False
        metadata = {
            "object_identifier_type": "UUID",
            "object_identifier_value": csv_row["objekti-uuid"],
            "original_name": csv_row["objekti-nimi"],
            "message_digest_algorithm": csv_row["tiiviste-tyyppi"],
            "message_digest": csv_row["tiiviste"],
            "alt_identifier_type": "local",
            "alt_identifier_value": csv_row["objekti-id"]
        }
        super().__init__(metadata)

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
            raise OSError("Digital object %s was not found!"
                          "" % (self.original_name))


class PremisEventMusicArchive(PremisEvent):
    """
    Music Archive specific PREMIS Event handler.
    """
    DETAIL_KEYS = ["tiiviste", "tiiviste-tyyppi", "tiiviste-aika",
                   "pon-korvattu-nimi", "objekti-nimi", "sip-tunniste",
                   "event-selite"]

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        self._detail_info = []

        start_time = datetime.datetime.strptime(
            csv_row["event-aika-alku"], "%Y-%m-%d %H:%M:%S"
            ).strftime("%Y-%m-%dT%H:%M:%S")
        end_time = None
        if csv_row["event-aika-loppu"].lower() != "null" and \
                csv_row["event-aika-loppu"] != csv_row["event-aika-alku"]:
            end_time = datetime.datetime.strptime(
                csv_row["event-aika-loppu"], "%Y-%m-%d %H:%M:%S"
                ).strftime("%Y-%m-%dT%H:%M:%S")

        event_datetime = start_time
        if end_time is not None:
            event_datetime = "{}/{}".format(start_time, end_time)

        metadata = {
            "event_identifier_type": "local",
            "event_identifier_value": csv_row["event-id"],
            "event_type": csv_row["event"],
            "event_outcome": csv_row["event-tulos"],
            "event_datetime": event_datetime
        }
        super().__init__(metadata)
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

        if self.event_type == "modification":
            return "Modification of digital object."

        if self.event_type == "metadata modification":
            return "Modification of metadata."

        raise NotImplementedError(
            "Not implemented event type '%s'." % (self.event_type))

    @property
    def event_outcome_detail(self):
        """Event outcome detail"""
        out = ""
        if self._detail_info[0]["event-selite"].lower() != "null":
            out = "%s\n\n" % self._detail_info[0]["event-selite"]

        if self.event_outcome != "success":
            return "%sEvent failed." % out

        if self.event_type == "message digest calculation":
            # The same algorithm exists in all elements of details
            out = "%sChecksum calculated with algorithm %s " \
                  "resulted the following checksums:" \
                  "" % (out, self._detail_info[0]["tiiviste-tyyppi"])
            for info in self._detail_info:
                checksum_time = datetime.datetime.strptime(
                    info["tiiviste-aika"], "%Y-%m-%d %H:%M:%S"
                    ).strftime("%Y-%m-%dT%H:%M:%S")
                out = "%s\n%s: %s (timestamp: %s)" \
                      "" % (out, info["objekti-nimi"],
                            info["tiiviste"], checksum_time)
            return out

        if self.event_type == "filename change":
            # There's only one element in details
            return "%sFilename changed.\nOld filename: %s\n" \
                   "New filename: %s\n" \
                   "" % (out,
                         self._detail_info[0]["pon-korvattu-nimi"],
                         self._detail_info[0]["objekti-nimi"])

        if self.event_type == "information package creation":
            # There's only one element in details
            return "%sSubmission information package created as: " \
                   "%s" % (out, self._detail_info[0]["sip-tunniste"])

        if self.event_type in ["modification"]:
            return "%sObject has been modified." % out

        if self.event_type in ["metadata modification"]:
            return "%sMetadata has been modified." % out

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
            "agent_identifier_value": "agent-" + csv_row["agent-id"],
            "agent_name": csv_row["agent-nimi"],
            "agent_type": csv_row["agent-tyyppi"],
        }
        super().__init__(metadata)


class PremisLinkingMusicArchive(PremisLinking):
    """
    Music Archive specific PREMIS Linking handler.
    """

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        super().__init__()
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
        super().add_object_link(identifier)
