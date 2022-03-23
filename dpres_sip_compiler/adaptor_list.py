"""
Dict of adaptor names and corresponding SIP metadata classes
"""
from dpres_sip_compiler.adaptors.musicarchive import \
    SipMetadataMusicArchive

ADAPTOR_DICT = {
    "musicarchive": SipMetadataMusicArchive
}
