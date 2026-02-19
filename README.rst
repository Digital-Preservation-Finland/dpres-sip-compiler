SIP Compiler
============

This is a tool which utilizes the Pre-Ingest Library according to given structured metadata and creates an OAIS Submission Information Package with a low number of commands. The tool can be extended with new adaptors, where different types of metadata are normalized and then given to the Pre-Ingest Library.

This tool helps especially smaller use cases in manual workflows, where the content and metadata is gathered in some agreed way, and then packaged and transferred to DPS.

For more information about Pre-Ingest Library, see:
https://github.com/Digital-Preservation-Finland/dpres-siptools-ng

Requirements
------------

Installation and usage requires Python 3.9 or newer.
The software is tested with Python 3.9 on AlmaLinux 9 release.

Installation using RPM packages (preferred)
-------------------------------------------

Installation on Linux distributions is done by using the RPM Package Manager.
See how to `configure the PAS-jakelu RPM repositories`_ to setup necessary software sources.

.. _configure the PAS-jakelu RPM repositories: https://www.digitalpreservation.fi/user_guide/installation_of_tools 

After the repository has been added, the package can be installed by running the following command::

    sudo dnf install python3-dpres-sip-compiler

Configuration
-------------

Copy file ``dpres_sip_compiler/conf/config_<adaptor>_template.conf`` to
``~/.config/dpres-sip-compiler/config.conf`` (or to some other path of your choice)
and modify organization name, contract ID and SIP signing key to it.
Here, ``<adaptor>`` is an agreed and implemented adaptor name.

The default location of the configuration file is
``~/.config/dpres-sip-compiler/config.conf``. If this is not the case,
you need to give the configuration file as a parameter when using this software.

See adaptor specific details below.

Adaptor Specific Details
------------------------

For details about adaptor specific configuration and content preparation,
select the adaptor below:

   * `Music Archive Finland <./doc/musicarchive.rst>`_
   * `The Finnish Postal Museum <./doc/postalmuseum.rst>`_
   * `Generic folder based adaptor <./doc/generic.rst>`_

Usage: Compile content
----------------------

Compile a given content by using the following command::

    sip-compiler compile <source-path> [<descriptive-metadata-path>...]

The following options can be used:

   * ``--tar-file <FILE>`` - Output tar file. If not given, the tar file will be
     in the current working path and it's name is based on the SIP identifier.
   * ``--content_id <CONTENT ID>`` - A semantic ID for the contents in the SIP.
   * ``--sip_id <SIP ID>`` - A technical ID for the the SIP, the METS OBJID.
   * ``--config <FILE>`` - Configuration file. If not given, the default config location
     is used.
   * ``--validation`` or ``--no-validation`` - Define whether validation is used
     during compilation. Validation is used by default.

The software creates a TAR file, which can be submitted to the Digital Preservation
Service.

Usage: Validate files separately
--------------------------------

Validation of the files can be used separately with the following command::

    sip-compiler validate <path-to-content>

The following options can be used:

   * ``--valid-output <FILE>`` - Target file to write result metadata for
     valid and supported files. Defaults to ``./validate_files_valid.jsonl``.
   * ``--invalid-output <FILE>`` - Target file to write result metadata for
     invalid or unsupported files. Defaults to
     ``./validate_files_invalid.jsonl``.
   * ``--summary`` or ``--no-summary`` - Write or do not write summary
     information to separate target files named
     ``<valid-output>_summary.jsonl`` and ``<invalid-output>_summary.jsonl``.
     By default, no summary is written.
   * ``--config <FILE>`` - Configuration file. If not given, the default
     config location is used.
   * ``--stdout`` - Print result metadata also to stdout.

If a target file already exists, the results will be appended to the end of
the file. This makes it possible to combine validation results of several
sets of files. It is also possible to use the same target file for valid and
invalid results. In such case, also the summary file is same for valid and
invalid results.

If the used adaptor defined in the configuration is set to skip some files in
compilation (for example hidden files), then these are also skipped in
validation without any notice in the target files.

Installation using Python Virtualenv for development purposes
-------------------------------------------------------------

Packages python3-devel, openssl-devel, swig and gcc are required in your system
to install M2Crypto, which is used for signing the packages with digital
signature.

Create a virtual environment::

    python3 -m venv venv

Run the following to activate the virtual environment::

    source venv/bin/activate

Install the required software with commands::

    pip install --upgrade pip==20.2.4 setuptools
    pip install -r requirements_github.txt
    pip install .

See the README from file-scraper repository for additional installation
requirements: https://github.com/Digital-Preservation-Finland/file-scraper/blob/master/README.rst

To deactivate the virtual environment, run ``deactivate``. To reactivate it,
run the ``source`` command above.

Copyright
---------
Copyright (C) 2022 CSC - IT Center for Science Ltd.

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU Lesser General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
this program.  If not, see <https://www.gnu.org/licenses/>.
