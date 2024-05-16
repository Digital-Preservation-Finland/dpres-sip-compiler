Release notes
=============

Unreleased
----------

- Update deprecated timezone calls

Version 0.17
------------

   * Handle normalization and migration events without the native file
     in Music Archive Adaptor.

Version 0.16
----------

   * Handle normalization and migration events with correct linking in
     Music Archive Adaptor.

Version 0.15
------------

Installation instructions for AlmaLinux 9 using RPM packages

Version 0.13-0.14
-----------------

   * Add RHEL9 RPM spec file.
   * Handle broken HTML files in Music Archive adaptor.
   * Code cleanups and syntax fixes.

Version 0.12
------------

   * Add a prefix to Music Archive's agent-IDs.

Version 0.11
------------

   * For Music Archive adaptor, add support for modification events and
     for given event detail.

Version 0.10
------------

   * Python 2.7 support officially removed.

Version 0.9
-----------

   * Add handling of checksum status (current, deprecated) in Music Archive adaptor.

Version 0.7-0.8
---------------

   * Make validation optional in packaging.
   * Fix handling of hidden files in Music Archive adaptor during validation.

Version 0.6
-----------

   * Add additional identifier to metadata for files in Music Archive adaptor.

Version 0.5
-----------

   * Adds the keys "filename" and "timestamp" to the validate command output.
   * Adds a summary option to the validate command. When used, writes summary
     information of the validation to separate output files.

Version 0.4
-----------

   * Adds a validate command that recursively identifies, validates,
     and scrapes metadata from files in given path.

Version 0.3
-----------

   * Fix handling of non-periodic event timestamps.

Version 0.2
-----------

   * Music archive adaptor fixes related to handling of hidden files,
     CSV structure, SIP identifier handling and minor details.

Version 0.1
-----------

   * Initial version of SIP Compiler.
   * Adaptor for Music Archive.
