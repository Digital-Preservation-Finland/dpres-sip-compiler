"""
Adaptor selector.
"""
from dpres_sip_compiler.adaptors.musicarchive import \
    SipMetadataMusicArchive


def select(workspace, config):
    """
    Select adaptor and prepare it.
    :workspace: Workspace path
    :config: Configure info
    :returns: SIP metadata object
    """
    if config.adaptor == "musicarchive":
        sip_meta = SipMetadataMusicArchive()
        sip_meta.populate(workspace, config)
    else:
        raise NotImplementedError(
            "Unsupported configuration! Maybe the adaptor name is incorrect "
            "in configuration file?")

    return sip_meta
