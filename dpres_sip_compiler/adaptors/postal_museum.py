"""Adaptor for Postal Museum."""
import os
import fnmatch
from collections.abc import Iterator
from uuid import uuid4
import xml_helpers.utils as h
import lxml.etree as ET
from dpres_sip_compiler.base_adaptor import SipMetadata, PremisObject
from dpres_sip_compiler.config import Config


class SipMetadataPostalMuseum(SipMetadata):
    """Class for collecting SIP metadata."""

    def populate(self, source_path: str, config: Config) -> None:
        """Recursively collect all file paths from given path."""
        files = []
        files += [os.path.join(looproot, filename)
                  for looproot, _, filenames in os.walk(source_path)
                  for filename in filenames
                  if fnmatch.fnmatch(filename, "*")]

        for filepath in files:
            metadata = {
                "object_identifier_type": "UUID",
                "object_identifier_value": str(uuid4())
            }
            p_object = PremisObject(metadata=metadata)
            # Use relative path for the objects
            p_object.filepath = os.path.relpath(filepath, source_path)
            self.add_object(p_object)

    def descriptive_metadata_sources(
        self,
        desc_paths: list[str],
        config: Config,
    ) -> Iterator[tuple[str, str]]:
        """
        Iterator for descriptive metadata.
        Parses root sections from XML files (containing multiple root
        elements) as serialized LIDO XML.

        :param desc_paths: Path to descriptive metadata files
        :param config: Additional needed configuration
        :returns: Iterator with tuple of descriptive metadata source
            format and string
        """
        for metadata_path in desc_paths:

            with open(metadata_path, 'rt', encoding='utf-8') as infile:
                textdata = infile.read()

            # Split text to individual lidoWrap elements to be able
            # to parse and serialize them as XML
            for lidowrap in textdata.split('<lido:lidoWrap'):

                # Skip leading XML declaration
                xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
                if lidowrap == xml_declaration:
                    continue

                lidowrap_elem = '<lido:lidoWrap' + lidowrap
                yield (config.desc_metadata_source_format,
                       h.serialize(ET.fromstring(lidowrap_elem)))
