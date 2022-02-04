SIP Compiler
------------

This is a tool which combines the commands of Pre-Ingest Tool according to
given structured metadata and creates an OAIS Submission Information Package
with a low number of commands. The tool can be extended with new adaptors,
where different types of metadata is normalized and then given to the
Pre-Ingest tool.

This tool helps especially smaller use cases in manual workflows, where
the content and metadata is gathered in some agreed way, and then
packaged and transferred to DPS.

For more information about Pre-Ingest tool, see:
https://github.com/Digital-Preservation-Finland/dpres-siptools

This tool is currently a work-in-progress project, and therefore
the possible command line interface updates may be incompatible with the
previous versions.

The tool currently supports only packaging of Music Archive data,
with an agreed content preparation rules.

Installation
------------

Installation and usage requires Python 2.7, or 3.6 or newer.

If Pre-Ingest Tool (dpres-siptools) is installed, then it is enough to
reactivate the environment, update the latest versions of the installed packages
and install this software::

    pip install -r requirements_github.txt --upgrade
    pip install .

If this is the case, you may skip the following installation guide. If there is
no Pre-Ingest Tool environment present, the following process is needed.

Packages openssl-devel, swig and gcc are required in your system to install
M2Crypto, which is used for signing the packages with digital signature.

For Python 2.7, get python-virtualenv software and create a virtual environment::

    yum install python-virtualenv
    virtualenv venv

For Python 3.6, create a virtual envirnoment::

    python3 -mvenv venv

Run the following to activate the virtual environment::

    source venv/bin/activate

Install the required software with command::

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

Copy file ``dpres_sip_compiler/conf/config_<adaptor>_template.conf`` to a proper
directory and modify organization name, contract ID and SIP signing key to it.
Here, ``<adaptor>`` is an agreed and implemented adaptor name.

For Music Archive data, the configuration template is located at
``dpres_sip_compiler/conf/config_musicarchive_template.conf``

Content Preparation
-------------------

The software assumes that the content to be packaged is in the given workspace
path.

For Music Archive data, the descriptive metadata of a package needs to be in
the workspace root named as ``*___metadata.xml`` (where ``*`` is any prefix).
There may be several descriptive metadata files. The structured administrative
metadata must be given as as single ``*___metadata.csv`` file. The CSV
structure has been agreed separately.

Usage
-----

Compile a given workspace with the content by using the following command::

    sip-complier compile <path-to-configuration-file> <path-to-workspace>

The software creates ``<identifier>.tar`` file in workspace, which can be submitted
to the Digital Preservation Service.

The software raises an exception and stops packaging immediately, if a problem
occurs. In such case, there may be some temporary files left in the workspace,
which must be deleted before trying again. The temporary files are currently
left for error debugging purposes. The temporary files can be deleted with the
following command::

    sip-compiler clean <path-to-workspace>

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
