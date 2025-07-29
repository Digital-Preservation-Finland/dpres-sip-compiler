"""
Dict of adaptor names and corresponding SIP metadata classes
"""
from dpres_sip_compiler.adaptors.musicarchive import \
    SipMetadataMusicArchive
from dpres_sip_compiler.adaptors.generic_adaptor import \
    GenericFolderStructure

ADAPTOR_DICT = {
    "generic": GenericFolderStructure,
    "musicarchive": SipMetadataMusicArchive
}
