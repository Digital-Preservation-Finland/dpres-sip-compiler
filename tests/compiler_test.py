"""Test SIP compilation.
"""
import os
import shutil
import lxml.etree
import pytest
from siptools.scripts.compile_structmap import compile_structmap
from dpres_sip_compiler.selector import select
from dpres_sip_compiler.compiler import (SipCompiler, compile_sip,
                                         clean_temp_files)
from dpres_sip_compiler.config import get_default_config_path


NAMESPACES = {
    'mets': 'http://www.loc.gov/METS/',
    'premis': 'info:lc/xmlns/premis-v2',
    'fi': 'http://digitalpreservation.fi/schemas/mets/fi-extensions',
    'audiomd': 'http://www.loc.gov/audioMD/',
}


def _get_provenance(workspace):
    """
    Find 'message digest calculation' event and 'Testaaja, Teppo' agent
    from workspace.

    :workspace: Workspace path
    :returns: Event and agent XML trees
    """
    event_paths = []
    agent_paths = []
    for root, _, files in os.walk(workspace, topdown=False):
        for name in files:
            if name.endswith("PREMIS%3AEVENT-amd.xml"):
                event_paths.append(os.path.join(root, name))
            if name.endswith("PREMIS%3AAGENT-amd.xml"):
                agent_paths.append(os.path.join(root, name))
    event_xml = None
    for path in event_paths:
        event_xml = lxml.etree.parse(path)
        if event_xml.xpath(
                ".//premis:eventType", namespaces=NAMESPACES)[0].text == \
                "message digest calculation":
            break
    agent_xml = None
    for path in agent_paths:
        agent_xml = lxml.etree.parse(path)
        if agent_xml.xpath(
                ".//premis:agentName", namespaces=NAMESPACES)[0].text == \
                "Testaaja, Teppo":
            break
    return (event_xml, agent_xml)


def test_technical(tmpdir, prepare_workspace):
    """
    Test technical metadata.

    The tests are run with the Music Archive adaptor, because in
    the time of writing, this is the only existing adaptor.

    Technical metadata is added based on existing CSV file.
    It is tested that the PREMIS metadata meets the info found in given CSV
    file. Also, existence of AudioMD is tested, because the test content
    includes an audio file. 
    """
    (workspace, config) = prepare_workspace(tmpdir)
    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace, config, sip_meta)
    compiler._create_technical_metadata()
    audio_path = None
    premis_path = None
    for root, _, files in os.walk(workspace, topdown=False):
        for name in files:
            if name.endswith("PREMIS%3AOBJECT-amd.xml"):
                premis_path = os.path.join(root, name)
            if name.endswith("AudioMD-amd.xml"):
                audio_path = os.path.join(root, name)
    premis_xml = lxml.etree.parse(premis_path)
    assert audio_path is not None
    assert premis_xml.xpath(".//premis:objectIdentifierType",
                            namespaces=NAMESPACES)[0].text == "UUID"
    assert premis_xml.xpath(".//premis:objectIdentifierValue",
                            namespaces=NAMESPACES)[0].text == \
        "882d63db-c9b6-4f44-83ba-901b300821cc"
    assert premis_xml.xpath(".//premis:messageDigestAlgorithm",
                            namespaces=NAMESPACES)[0].text == "MD5"
    assert premis_xml.xpath(".//premis:messageDigest",
                            namespaces=NAMESPACES)[0].text == "abc123"
    assert premis_xml.xpath(".//premis:originalName",
                            namespaces=NAMESPACES)[0].text == "testfile1.wav"
    assert premis_xml.xpath(".//premis:formatName",
                            namespaces=NAMESPACES)[0].text == "audio/x-wav"


def test_provenance(tmpdir, prepare_workspace):
    """
    Test provenance metadata.

    The tests are run with the Music Archive adaptor, because in
    the time of writing, this is the only existing adaptor.

    Provenance metadata is added based on existing CSV file.
    It is tested that the content of an event and an agent added to METS
    meet the info found in the given CSV file. 
    """
    (workspace, config) = prepare_workspace(tmpdir)
    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace, config, sip_meta)
    compiler._create_technical_metadata()
    compiler._create_provenance_metadata()
    (event_xml, agent_xml) = _get_provenance(workspace)
    assert event_xml.xpath(
        ".//premis:eventType", namespaces=NAMESPACES)[0].text == \
        "message digest calculation"
    assert event_xml.xpath(
        ".//premis:eventDateTime", namespaces=NAMESPACES)[0].text == \
        "2022-02-02T00:00:00"
    assert event_xml.xpath(".//premis:eventOutcome",
                           namespaces=NAMESPACES)[0].text == "success"
    assert event_xml.xpath(
        ".//premis:eventDetail", namespaces=NAMESPACES)[0].text == \
        "Checksum calculation for digital objects."
    assert event_xml.xpath(
        ".//premis:eventOutcomeDetailNote",
        namespaces=NAMESPACES)[0].text == \
        "Checksum calculated with algorithm MD5 resulted the following " \
        "checksums:\ntestfile1.wav: abc123"
    assert event_xml.xpath(".//premis:linkingObjectIdentifierType",
                           namespaces=NAMESPACES)[0].text == "UUID"
    assert event_xml.xpath(
        ".//premis:linkingObjectIdentifierValue",
        namespaces=NAMESPACES)[0].text == \
        "882d63db-c9b6-4f44-83ba-901b300821cc"
    assert event_xml.xpath(".//premis:linkingObjectRole",
                           namespaces=NAMESPACES)[0].text == "target"
    assert event_xml.xpath(".//premis:linkingAgentIdentifierType",
                           namespaces=NAMESPACES)[0].text == "local"
    assert event_xml.xpath(".//premis:linkingAgentIdentifierValue",
                           namespaces=NAMESPACES)[0].text == "1"
    assert event_xml.xpath(".//premis:linkingAgentRole",
                           namespaces=NAMESPACES)[0].text == "implementer"
    assert agent_xml.xpath(".//premis:agentIdentifierType",
                           namespaces=NAMESPACES)[0].text == "local"
    assert agent_xml.xpath(".//premis:agentIdentifierValue",
                           namespaces=NAMESPACES)[0].text == "1"
    assert agent_xml.xpath(
        ".//premis:agentName", namespaces=NAMESPACES)[0].text == \
        "Testaaja, Teppo"
    assert agent_xml.xpath(".//premis:agentType",
                           namespaces=NAMESPACES)[0].text == "person"


def test_descriptive(tmpdir, prepare_workspace):
    """
    Test that correct number of descriptive metadata sections exists.
    """
    (workspace, config) = prepare_workspace(tmpdir, "workspace1")
    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace, config, sip_meta)
    compiler._import_descriptive_metadata()
    count = 0
    for root, _, files in os.walk(workspace, topdown=False):
        for name in files:
            if name.endswith("dmdsec.xml"):
                count = count + 1
    assert count == 2


def test_compile_metadata(tmpdir, prepare_workspace):
    """Test METS compilation.

    The following cases about the METS and packaging are tested:
    (1) mets.xml exists.
    (2) METS Header attribute values (creator agent name, type and role)
        are correct.
    (3) Mets root attributes (contract id and objid) are correct.
    """
    (workspace, config) = prepare_workspace(tmpdir)
    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace, config, sip_meta)
    compiler._create_technical_metadata()
    compiler._compile_metadata()

    mets_xml = lxml.etree.parse(os.path.join(workspace, "mets.xml"))
    assert os.path.isfile(os.path.join(workspace, "mets.xml"))
    assert mets_xml.xpath("/mets:mets/mets:metsHdr/mets:agent/mets:name",
                          namespaces=NAMESPACES)[0].text == "Archive X"
    assert mets_xml.xpath("/mets:mets/mets:metsHdr/mets:agent/@TYPE",
                          namespaces=NAMESPACES)[0] == "ORGANIZATION"
    assert mets_xml.xpath("/mets:mets/mets:metsHdr/mets:agent/@ROLE",
                          namespaces=NAMESPACES)[0] == "CREATOR"
    assert mets_xml.xpath(
        "/mets:mets/@fi:CONTRACTID", namespaces=NAMESPACES)[0] == \
        "urn:uuid:474418c5-79a6-4e86-bfc8-5aed0a3337d7"
    assert mets_xml.xpath(
        "/mets:mets/@OBJID", namespaces=NAMESPACES)[0] == \
        "Package_2022-02-07_123"

def test_compile_package(tmpdir, prepare_workspace):
    """
    Test package and METS creation.

    The following cases about the packaging are tested:
    (1) mets.xml exists.
    (2) signature.sig exists.
    (3) tar file with correct name exists.
    """
    (workspace, config) = prepare_workspace(tmpdir)
    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace, config, sip_meta)
    compiler._create_technical_metadata()
    compiler._compile_metadata()
    compiler._compile_package()
    mets_xml = lxml.etree.parse(os.path.join(workspace, "mets.xml"))
    assert os.path.isfile(os.path.join(workspace, "mets.xml"))
    assert os.path.isfile(os.path.join(workspace, "signature.sig"))
    assert os.path.isfile(os.path.join(workspace,
                                       "Package_2022_02_07_123.tar"))


def test_compile_sip(tmpdir, prepare_workspace):
    """
    Test SIP compilation.

    The following cases about the SIP comilation are tested:
    (1) mets.xml exists.
    (2) signature.sig exists.
    (3) tar file with correct name exists.
    (4) Number of different metadata sections in METS is correct.
    """
    (workspace, _) = prepare_workspace(tmpdir, "workspace1")
    compile_sip(workspace, "tests/data/musicarchive/config.conf")
    mets_xml = lxml.etree.parse(os.path.join(workspace, "mets.xml"))
    assert os.path.isfile(os.path.join(workspace, "mets.xml"))
    assert os.path.isfile(os.path.join(workspace, "signature.sig"))
    assert os.path.isfile(os.path.join(workspace,
                                       "Package_2022_02_07_123.tar"))
    assert len(mets_xml.xpath(".//mets:dmdSec",
                              namespaces=NAMESPACES)) == 2
    assert len(mets_xml.xpath(".//mets:techMD//premis:object",
                              namespaces=NAMESPACES)) == 4
    assert len(mets_xml.xpath(".//mets:techMD//audiomd:AUDIOMD",
                              namespaces=NAMESPACES)) == 1
    assert len(mets_xml.xpath(".//mets:digiprovMD//premis:event",
                              namespaces=NAMESPACES)) == 22
    assert len(mets_xml.xpath(".//mets:digiprovMD//premis:agent",
                              namespaces=NAMESPACES)) == 13
    assert len(mets_xml.xpath(".//mets:file",
                              namespaces=NAMESPACES)) == 4
    assert len(mets_xml.xpath(".//mets:structMap",
                              namespaces=NAMESPACES)) == 1


def test_default_config(tmpdir, prepare_workspace):
    """
    Test that organization name from a config file located in
    default location is found in METS.
    """
    (workspace, _) = prepare_workspace(tmpdir, "workspace1")
    conf_path = get_default_config_path()
    conf_dir = os.path.dirname(conf_path)
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    shutil.copy("tests/data/musicarchive/config.conf", conf_path)
    compile_sip(workspace)
    mets_xml = lxml.etree.parse(os.path.join(workspace, "mets.xml"))
    assert os.path.isfile(os.path.join(workspace, "mets.xml"))
    assert os.path.isfile(os.path.join(workspace, "signature.sig"))
    assert os.path.isfile(os.path.join(workspace,
                                       "Package_2022_02_07_123.tar"))
    assert mets_xml.xpath("/mets:mets/mets:metsHdr/mets:agent/mets:name",
                          namespaces=NAMESPACES)[0].text == "Archive X"


def _count_temp_files(workspace):
    """Count temporary files in workspace.
    """
    count = 0
    for root, _, files in os.walk(workspace, topdown=False):
        for name in files:
            if not name.endswith(("___metadata.xml", "___metadata.csv",
                                  "testfile1.wav")):
                count = count + 1
    return count


def test_automated_cleanup(tmpdir, prepare_workspace):
    """
    Test that calling the steps multiple times remove the temporary files
    resulted from the previous call.
    """
    (workspace, config) = prepare_workspace(tmpdir)
    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace, config, sip_meta)
    compiler.create_sip()
    count = _count_temp_files(workspace)
    compiler.create_sip()
    assert _count_temp_files(workspace) == count

    compile_sip(workspace, "tests/data/musicarchive/config.conf")
    compile_sip(workspace, "tests/data/musicarchive/config.conf")
    assert _count_temp_files(workspace) == count


@pytest.mark.parametrize("temp_files, file_endings, file_names", [
    (("foo-PREMIS%%3AOBJECT-amd.xml",
      "foo-NISOIMG-amd.xml",
      "foo-AGENTS-amd.json",
      "import-object-md-references.jsonl",
      "create-mix-md-references.jsonl",
      "premis-event-md-references.jsonl",
      "import-description-md-references.jsonl",
      "foo-scraper.json", "foo-dmdsec.xml", "foo.tar",
      "filesec.xml", "structmap.xml", "mets.xml",
      "signature.sig"), None, None),
    (("foo-matching-ending", "foo-another-match"),
     ("matching-ending", "another-match"), None),
    (("foo-matching-file", "foo-another-match"), None,
     ("foo-matching-file", "foo-another-match"))
])
def test_clean_temp_files(tmpdir, temp_files, file_endings, file_names):
    """
    Test cleaning of all temporary files and a subset. The files
    matching to given file endings or file names are removed.

    :temp_files: Temporary files to be created
    :file_endings: File endings to search
    :file_names: File namess to search
    """
    for temp_file in temp_files:
        temp_path = os.path.join(str(tmpdir), temp_file)
        open(temp_path, "w").close()
        assert os.path.exists(temp_path)

    clean_temp_files(str(tmpdir), file_endings, file_names)

    for temp_file in temp_files:
        temp_path = os.path.join(str(tmpdir), temp_file)
        assert not os.path.exists(temp_path)


def test_clean_workspace(tmpdir, prepare_workspace):
    """
    Test workspace cleaning. First create temporary files by calling
    different metadata creation steps. Eventually remove those.
    Check that only source files exist.
    """
    (workspace, config) = prepare_workspace(tmpdir)
    sip_meta = select(workspace, config)
    compiler = SipCompiler(workspace, config, sip_meta)
    compiler._create_technical_metadata()
    compiler._create_provenance_metadata()
    compiler._import_descriptive_metadata()
    compiler._compile_metadata()
    clean_temp_files(workspace)
    assert _count_temp_files(workspace) == 0
