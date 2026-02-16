"""Generic adaptor."""
import os
import fnmatch
from uuid import uuid4
from dpres_sip_compiler.base_adaptor import SipMetadata, PremisObject


class GenericFolderStructure(SipMetadata):
    """Class for collecting filepaths."""

    def populate(self, source_path, config):
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

    def descriptive_files(self,
                          desc_paths=None,
                          config=None):
        """
        Iterator for descriptive metadata files.

        :desc_paths: List of descriptive metadata files
        :config: Additional needed configuration
        :returns: Descriptive metadata file
        """
        yield from desc_paths
