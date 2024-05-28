"""
Dict of adaptor names and corresponding SIP metadata classes
"""
from dpres_sip_compiler.adaptors.musicarchive import \
    SipMetadataMusicArchive
from dpres_sip_compiler.adaptors.generic_adaptor import \
    GenericFolderStructure

ADAPTOR_DICT = {
    "musicarchive": SipMetadataMusicArchive
}

ADAPTOR_NG_DICT = {
    "generic": GenericFolderStructure
}
