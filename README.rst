SIP Compiler
============

This is a tool which combines the commands of Pre-Ingest Tool according to
given structured metadata and creates an OAIS Submission Information Package
with a low number of commands. The tool can be extended with new adaptors,
where different types of metadata are normalized and then given to the
Pre-Ingest Tool.

This tool helps especially smaller use cases in manual workflows, where
the content and metadata is gathered in some agreed way, and then
packaged and transferred to DPS.

For more information about Pre-Ingest Tool, see:
https://github.com/Digital-Preservation-Finland/dpres-siptools

This tool is currently a work-in-progress project, and therefore
the possible command line interface updates may be incompatible with the
previous versions.

Installation
------------

Installation and usage requires Python 2.7, or 3.6 or newer.

If Pre-Ingest Tool (dpres-siptools) is installed, then it is enough to
reactivate the environment, update the latest versions of the installed packages
and install this software with the following commands::

    source venv/bin/activate       # Example command
    pip install -r requirements_github.txt --upgrade
    pip install .

If this is the case, you may skip the following installation guide. If there is
no Pre-Ingest Tool environment present, the following process is needed.

Packages openssl-devel, swig and gcc are required in your system to install
M2Crypto, which is used for signing the packages with digital signature.

For Python 2.7, get python-virtualenv software and create a virtual environment::

    yum install python-virtualenv
    virtualenv venv

For Python 3.6 or newer, create a virtual environment::

    python3 -m venv venv

Run the following to activate the virtual environment::

    source venv/bin/activate

Install the required software with commands::

    pip install --upgrade pip setuptools          # Only for Python 2.7
    pip install --upgrade pip==20.2.4 setuptools  # Only for Python 3.6 or newer
    pip install -r requirements_github.txt
    pip install .

See the README from file-scraper repository for additional installation
requirements: https://github.com/Digital-Preservation-Finland/file-scraper/blob/master/README.rst

To deactivate the virtual environment, run ``deactivate``. To reactivate it,
run the ``source`` command above.

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

The tool currently supports only packaging of data of Music Archive Finland,
with content preparation rules which have been agreed in advance.

Usage
-----

Compile a given content by using the following command::

    sip-compiler compile <path-to-content>

The following options can be used:

   * ``--tar-file <FILE>`` - Output tar file. If not given, the tar file will be
     in the current working path and it's name is based on the SIP identifier.
   * ``--temp-path <PATH>`` - Path for temporary files. If not given, the temporary
     path will be a timestamp path in current working directory.
   * ``--config <FILE>`` - Configuration file. If not given, the default config location
     is used.

The software creates a TAR file, which can be submitted to the Digital Preservation
Service. The path to temporary files is deleted if it was created during the process
and no files remain in it after cleaning.

The software raises an exception and stops packaging immediately, if a problem
occurs. In such case, there may be some temporary files left in the path for
temporary files. These files are automatically removed if trying again with the
same temporary path. The temporary files can also be deleted with the following
command::

    sip-compiler clean <path-to-temp-files>

The following options can be used:

   * ``--delete-path`` If used and the path is empty, it will be deleted.

This also removes possible ``mets.xml`` and ``signature.sig``.

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
