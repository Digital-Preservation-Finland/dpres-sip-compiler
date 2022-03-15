Configuration
-------------

For Music Archive data, the configuration template is located at
``dpres_sip_compiler/conf/config_musicarchive_template.conf``
Copy the file to any directory and modify organization name,
contract ID and SIP signing key to it.

Content Preparation
-------------------

For Music Archive data, the descriptive metadata of a package needs to be in
the workspace root named as ``*___metadata.xml`` (where ``*`` is any string).
There may be several descriptive metadata files. The structured administrative
metadata must be given as as single ``*___metadata.csv`` file, which needs
to be in the workspace root. The CSV structure has been agreed in advance.
These files are utilized in packaging, but these will not be included in the
package as separate digital objects.
