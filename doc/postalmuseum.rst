Additional Info for Handling the Data of the Finnish Postal Museum
==================================================================

Here are additional details about the configuration and content preparations
for the data of the Finnish Postal Museum.

Configuration
-------------

For the data of the Postal Museum, the configuration template is located
at ``dpres_sip_compiler/conf/config_postalmuseum_template.conf``
Copy the file to ``~/.config/dpres-sip-compiler/config.conf``
(or to some other path of your choice) and modify organization name,
contract ID and SIP signing key to it.

Content Preparation
-------------------

For the data of the Postal Museum, the descriptive metadata of a package
needs to be in an XML file containing multiple LIDO metadata sections. The
file is expected not to have a root element, but raher contain separate XML
sections bundled together into a file.

The content files must be prepared in a folder structure representing the
final SIP.

When running the script, the CONTENTID and SIP ID (i.e. METS OBJID) should
be used as options to provide necessary identifiers to the information
package.
