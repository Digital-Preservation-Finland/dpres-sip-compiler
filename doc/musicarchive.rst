Additional Info for Handling the Data of Music Archive Finland
==============================================================

Here are additional details about the configuration and content preparations
for the data of Music Archive Finland.

Configuration
-------------

For the data of Music Archive Finland, the configuration template is located
at ``dpres_sip_compiler/conf/config_musicarchive_template.conf``
Copy the file to ``~/.config/dpres-sip-compiler/config.conf``
(or to some other path of your choice) and modify organization name,
contract ID and SIP signing key to it.

Content Preparation
-------------------

For the data of Music Archive Finland, the descriptive metadata of a package
needs to be in the source path root named as ``*___metadata.xml`` (where
``*`` is any string). There may be several descriptive metadata files. The
structured administrative metadata must be given as as single
``*___metadata.csv`` file, which needs to be in the source path root. The
CSV structure has been agreed in advance. These files are utilized in
packaging, but these will not be included in the package as separate digital
objects.

Skipped Content
---------------

Specially named metadata XML and CSV files described in previous chapter,
and also hidden files and directories, will not be included as separate
digital objects in the package in compilation. These files are also
skipped in validation without producing any note in the validation results.
