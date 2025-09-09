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
from file_scraper.defaults import UNAP
from dpres_sip_compiler.base_adaptor import (
    SipMetadata, PremisObject, PremisEvent, PremisAgent,
    PremisLinking)
from dpres_sip_compiler.constants import (
    EVENT_DIGEST,
    EVENT_CHANGE,
    EVENT_CONVERSION,
    EVENT_CREATION,
    EVENT_MODIFICATION,
    EVENT_META_MODIFICATION,
    EVENT_NORMALIZATION,
    EVENT_MIGRATION,
    FILE_OUTCOME_SOURCE,
    FILE_USE_IGNORE_VALIDATION,
    PREMIS_ADDRESS,
)


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
        self.content_id = self.objid

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
            if p_object.alt_identifier_type and p_object.alt_identifier_value:
                self.add_object_alt_id(
                    obj_identifier=p_object.identifier,
                    alt_identifier_type=p_object.alt_identifier_type,
                    alt_identifier=p_object.alt_identifier_value,
                )
        p_event = PremisEventMusicArchive(csv_row)
        self.add_event(p_event)
        self.premis_events[p_event.identifier].add_detail_info(
            csv_row)
        self.add_agent(PremisAgentMusicArchive(csv_row))
        self.add_linking(p_linking=PremisLinkingMusicArchive(csv_row),
                         object_id=csv_row["objekti-uuid"],
                         object_role=csv_row["poo-sip-obj-x-rooli-selite"],
                         agent_id="agent-"+csv_row["agent-id"],
                         agent_role=csv_row["agent-rooli"])
        # -1 and -3 are the two legitimate values for representation object.
        if csv_row["poo-vastinpari-obj-status"] in ["-1", "-3"]:
            r_object = PremisRepresentationMusicArchive(csv_row)
            r_object.find_target_path(source_path)
            self.add_digiprov_representation_object(r_object)
            if r_object.alt_identifier_type and r_object.alt_identifier_value:
                self.add_object_alt_id(
                    obj_identifier=r_object.identifier,
                    alt_identifier_type=r_object.alt_identifier_type,
                    alt_identifier=r_object.alt_identifier_value,
                )
        if (
            p_event.event_type == EVENT_CONVERSION
            and csv_row["poo-sip-obj-x-rooli-selite"] == FILE_OUTCOME_SOURCE
        ):
            self.add_object_attribute(
                obj_identifier=p_object.identifier,
                name="use",
                value=FILE_USE_IGNORE_VALIDATION,
            )

    def descriptive_files(self, desc_path=None, config=None):
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

    def scrape_objects(self, source_path: str, validation: bool) -> None:
        """To scrape objects and store their scraper results.

        :param source_path: Source path for the objects.
        :param validation: Whether to enable well_formed check or not.
        """
        for obj_identifier, obj in self.premis_objects.items():
            scraper = Scraper(
                filename=os.path.join(source_path, obj.filepath),
                mimetype=obj.format_name,
                version=obj.format_version,
            )
            scraper.scrape(check_wellformed=validation)
            # Special case for musicarchive
            if scraper.mimetype == "text/html":
                if validation is False:
                    # If validation was disabled, we'll enable for this
                    # special case handling.
                    scraper = Scraper(
                        filename=os.path.join(source_path, obj.filepath),
                        mimetype=obj.format_name,
                        version=obj.format_version,
                    )
                    scraper.scrape(check_wellformed=True)
                if scraper.well_formed is False:
                    scraper.mimetype = "text/plain; alt-format=text/html"
                    scraper.version = UNAP

            scraper_result = {
                "streams": scraper.streams,
                "info": scraper.info,
                "mimetype": scraper.mimetype,
                "version": scraper.version,
                "checksum": scraper.checksum().lower(),
                "grade": scraper.grade(),
            }
            self.scraper_results[obj_identifier] = scraper_result

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
                    namespaces={'premis': PREMIS_ADDRESS})) > 1:
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
        namespaces={'premis': PREMIS_ADDRESS})
    if not format_elems:
        return mets

    for format_elem in format_elems:
        techmd_id = format_elem.xpath(
            "ancestor::mets:techMD/@ID",
            namespaces={'mets': 'http://www.loc.gov/METS/'})[0]
        file_path = find_path_by_techmd_id(mets, techmd_id)

        scraper = Scraper(os.path.join(source_path, file_path))
        scraper.scrape(check_wellformed=True)

        if scraper.well_formed is False:
            set_format_plaintext(
                format_elem,
                "text/plain; alt-format=text/html")
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


def set_format_plaintext(format_element, new_value):
    """
    Change formatName value to given value and remove formatVersion.
    :format_element: Object. Premis format element.
    :new_value: String. New value of formatName element.
    """
    format_name_element = format_element.xpath(
        ".//premis:formatName",
        namespaces={'premis': PREMIS_ADDRESS})
    format_name_element[0].text = new_value

    format_version_element = format_element.xpath(
        ".//premis:formatVersion",
        namespaces={'premis': PREMIS_ADDRESS})
    if format_version_element:
        format_version_element[0].getparent().remove(format_version_element[0])


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
            "alt_identifier_value": csv_row["objekti-id"],
            "bit_level": False
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

    time_parse_format = "%Y-%m-%d %H:%M:%S"
    time_output_format = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        self._detail_info = []

        start_time = datetime.datetime.strptime(
            csv_row["event-aika-alku"], self.time_parse_format
            ).strftime(self.time_output_format)
        end_time = None
        if csv_row["event-aika-loppu"].lower() != "null" and \
                csv_row["event-aika-loppu"] != csv_row["event-aika-alku"]:
            end_time = datetime.datetime.strptime(
                csv_row["event-aika-loppu"], self.time_parse_format
                ).strftime(self.time_output_format)

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
        if self.event_type == EVENT_DIGEST:
            return "Checksum calculation for digital objects."

        if self.event_type == EVENT_CHANGE:
            return "Filename change."

        if self.event_type == EVENT_CREATION:
            return "Creation of submission information package."

        if self.event_type == EVENT_MODIFICATION:
            return "Modification of digital object."

        if self.event_type == EVENT_META_MODIFICATION:
            return "Modification of metadata."

        if self.event_type == EVENT_NORMALIZATION:
            return (
                "Normalization of digital object in an unsupported file "
                "format to a sustainable format for digital preservation, "
                "replacing the source object."
            )

        if self.event_type == EVENT_MIGRATION:
            return (
                "Migration of digital object to another file format, "
                "replacing the source object."
            )

        if self.event_type == EVENT_CONVERSION:
            return (
                "Conversion of digital object to another file format, "
                "creating a new derivative version of the source object."
            )

        raise NotImplementedError(
            f"Not implemented event type '{self.event_type}'."
        )

    @property
    def event_outcome_detail(self):
        """Event outcome detail"""
        out = ""
        if self._detail_info[0]["event-selite"].lower() != "null":
            out = "%s\n\n" % self._detail_info[0]["event-selite"]

        if self.event_outcome != "success":
            return "%sEvent failed." % out

        if self.event_type == EVENT_DIGEST:
            # The same algorithm exists in all elements of details
            out = "%sChecksum calculated with algorithm %s " \
                  "resulted the following checksums:" \
                  "" % (out, self._detail_info[0]["tiiviste-tyyppi"])
            for info in self._detail_info:
                checksum_time = datetime.datetime.strptime(
                        info["tiiviste-aika"], self.time_parse_format
                    ).strftime(self.time_output_format)
                out = "%s\n%s: %s (timestamp: %s)" \
                      "" % (out, info["objekti-nimi"],
                            info["tiiviste"], checksum_time)
            return out

        if self.event_type == EVENT_CHANGE:
            # There's only one element in details
            return "%sFilename changed.\nOld filename: %s\n" \
                   "New filename: %s\n" \
                   "" % (out,
                         self._detail_info[0]["pon-korvattu-nimi"],
                         self._detail_info[0]["objekti-nimi"])

        if self.event_type == EVENT_CREATION:
            # There's only one element in details
            return "%sSubmission information package created as: " \
                   "%s" % (out, self._detail_info[0]["sip-tunniste"])

        if self.event_type in [EVENT_MODIFICATION]:
            return "%sObject has been modified." % out

        if self.event_type in [EVENT_META_MODIFICATION]:
            return "%sMetadata has been modified." % out

        if self.event_type == EVENT_NORMALIZATION:
            return "%sFile format has been normalized. Outcome object " \
                "has been created as a result." % out

        if self.event_type == EVENT_MIGRATION:
            return "%sFile format has been migrated. Outcome object has " \
                "been created as a result." % out

        if self.event_type == EVENT_CONVERSION:
            return (
                f"{out}File format has been converted. "
                "Outcome object has been created as a result."
            )

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
        self.object_role = csv_row["poo-sip-obj-x-rooli-selite"]
        self.counterpart_obj_uuid = csv_row["poo-vastinpari-obj-uuid"]
        self.counterpart_obj_id = csv_row["poo-vastinpari-obj-id"]
        self.counterpart_obj_name = csv_row["poo-vastinpari-obj-nimi"]
        self.counterpart_obj_status = csv_row["poo-vastinpari-obj-status"]

    def add_object_link(self, identifier, object_role):
        """
        Add object to linking. Skip object adding if event type is
        'information package creation'.
        :identifier: PREMIS Object identifier
        :object_role: Object role in event.
        """
        if self._event_type == EVENT_CREATION:
            return
        # -1 and -3 are the two legitimate values.
        if self.counterpart_obj_status in ["-1", "-3"]:
            super().add_object_link(self.counterpart_obj_uuid, "source")
        super().add_object_link(identifier, object_role)


class PremisRepresentationMusicArchive(PremisObject):
    """Music Archive specific PREMIS Representation handler."""
    def __init__(self, csv_row):
        """Initialize.
        :csv_row: One row from a CSV file.
        """
        metadata = {
            "object_identifier_type": "UUID",
            "object_identifier_value": csv_row["poo-vastinpari-obj-uuid"],
            "original_name": csv_row["poo-vastinpari-obj-nimi"],
            "alt_identifier_type": "local",
            "alt_identifier_value": csv_row["poo-vastinpari-obj-id"],
            "object_status": csv_row["poo-vastinpari-obj-status"],
            "outcome_filename": csv_row["objekti-nimi"]
        }
        super().__init__(metadata)

    def find_target_path(self, source_path):
        """
        Find file path to outcome object.
        :source_path: Source data path.
        """
        for root, _, files in os.walk(source_path):
            if self.outcome_filename in files:
                target_path = os.path.relpath(os.path.join(
                    root, self.outcome_filename), source_path)
                self.filepath = target_path
                return
        raise OSError(f"Digital object {self.outcome_filename} was not found!")
