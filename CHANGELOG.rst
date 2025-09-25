Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

Fixed
^^^^^

- USE attribute for bit-level files is now set to correct value

2.1.0 - 2025-09-16
------------------

Added
^^^^^

- Skip creation of content type specific technical metadata for source files in migration and normalization events


2.0.0 - 2025-09-12
------------------

Added
^^^^^

- Replace backend tool dpres-siptools with dpres-siptools-ng and dpres-mets-builder for SIP creation in all adaptors
- Remove the compile-ng command as the compile command now uses the new backend tools
- Remove the clean command as temporary files are not created anymore
- Add option to include several descriptive metadata paths to the compile command
- Remove option temp-path from the compile command
- Remove configuration parameter desc_root_remove

1.0.0 - 2025-07-25
------------------

Added
^^^^^

- Add additional logic how digital object's USE attribute is assigned

Changed
^^^^^^^

- Clean up Makefile's install command from unnecessary parts.
- Support Musicarchive adaptor usage in compile-ng.
- Support conversion events in compile-ng.
- Change Musicarchive adaptor's placeholder "xxx" value for "-1" and "-3" that is used for object linking.
- Moved the project to use Keep a Changelog format and Semantic Versioning

0.20
----

- Update the compile-ng command to work with the published stable version of siptools-ng

0.19
----

- Add functionality to use dpres-siptools-ng for SIP compilation in a basic use case.

0.18
----

- Link representation objects to events on a PREMIS level
- Update deprecated timezone calls

0.17
----

- Handle normalization and migration events without the native file
  in Music Archive Adaptor.

0.16
----

- Handle normalization and migration events with correct linking in
  Music Archive Adaptor.

0.15
----

Installation instructions for AlmaLinux 9 using RPM packages

0.14
----

- Add RHEL9 RPM spec file.
- Handle broken HTML files in Music Archive adaptor.
- Code cleanups and syntax fixes.

0.12
----

- Add a prefix to Music Archive's agent-IDs.

0.11
----

- For Music Archive adaptor, add support for modification events and
  for given event detail.

0.10
----

- Python 2.7 support officially removed.

0.9
---

- Add handling of checksum status (current, deprecated) in Music Archive adaptor.

0.8
---

- Make validation optional in packaging.
- Fix handling of hidden files in Music Archive adaptor during validation.

0.6
---

- Add additional identifier to metadata for files in Music Archive adaptor.

0.5
---

- Adds the keys "filename" and "timestamp" to the validate command output.
- Adds a summary option to the validate command. When used, writes summary
  information of the validation to separate output files.

0.4
---

- Adds a validate command that recursively identifies, validates,
  and scrapes metadata from files in given path.

0.3
---

- Fix handling of non-periodic event timestamps.

0.2
---

- Music archive adaptor fixes related to handling of hidden files,
  CSV structure, SIP identifier handling and minor details.

0.1
---

- Initial version of SIP Compiler.
- Adaptor for Music Archive.
