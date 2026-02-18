Additional Info for Handling the Generic Adaptor
================================================

Here are additional details about the configuration and content preparations
for the generic, folder based, adaptor.

Configuration
-------------

An empty configuration template is located at
``dpres_sip_compiler/conf/config_template.conf``
Copy the file to ``~/.config/dpres-sip-compiler/config.conf``
(or to some other path of your choice) and add the missing values (examples
are provided in the template).

Content Preparation
-------------------

The content files must be prepared in a folder structure representing the
final SIP. The descriptive metadata must be provided as valid XML files.

When running the script, the CONTENTID and SIP ID (i.e. METS OBJID) can
be used as options to provide useful identifiers to the information
package.
