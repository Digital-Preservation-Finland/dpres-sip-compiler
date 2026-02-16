"""Adaptor for Postal Museum."""
import os
import fnmatch
from collections.abc import Iterator
from typing import List, Optional
from uuid import uuid4
import xml_helpers.utils as h
from dpres_sip_compiler.base_adaptor import SipMetadata, PremisObject
from dpres_sip_compiler.config import Config


class SipMetadataPostalMuseum(SipMetadata):
    """Class for collecting SIP metadata."""

    def populate(self, source_path: str, config: Config):
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

    def descriptive_strings(
        self,
        desc_paths: List[str],
        config: Optional[Config] = None
    ) -> Iterator[str]:
        """
        Iterator for descriptive metadata. Returns metadata sections
        from XML files' root element as serialized XML.

        :param desc_paths: Path to descriptive metadata files
        :param config: Additional needed configuration
        :returns: Iterator
        """
        for metadata_path in desc_paths:
            root = h.readfile(metadata_path).getroot()
            for elem in root:
                yield h.serialize(elem)
