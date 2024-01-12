"""Common fuctions and fixtures for tests.
"""
import os
import tarfile
import lxml
from click.testing import CliRunner
import pytest
from dpres_sip_compiler.config import Config
from dpres_sip_compiler.cmd import cli


@pytest.fixture(scope="function")
def pick_files_tar():
    """
    List all files included in a TAR file and extract the given files.
    """
    def _pick_files_tar(tar_file, target=None, extract_list=None):
        """
        List all files included in a TAR file and extract the given files.
        :tar_file: TAR file.
        :target: Target directory to extract files.
        :extract_list: List of files to extract.
        """
        with tarfile.open(tar_file) as tar:
            if extract_list is not None:
                tar.extractall(
                    path=target,
                    members=[member for member in tar.getmembers()
                             if member.name in extract_list])
            return tar.getnames()
        return []

    return _pick_files_tar


@pytest.fixture(scope="function")
def prepare_workspace():
    """
    Prepare temporary workspace.
    """
    def _prepare(tmp_path, source="source2"):
        """
        Prepare temporary workspace.
        :tmp_path: Temporary test path
        :source: Source objects from test data
        :returns: Source path, TAR file path, temporary path and configuration
        """
        source_path = os.path.join("tests/data/musicarchive", source)
        config = Config()
        config.configure("tests/data/musicarchive/config.conf")
        tar_file = os.path.join(str(tmp_path), "sip.tar")
        return (source_path, tar_file, str(tmp_path), config)

    return _prepare


@pytest.fixture(scope="function")
def run_cli():
    """Executes given Click interface with given arguments
    """
    def _run_cli(args):
        """
        Execute Click command with given arguments.
        :returns: Command result
        """
        runner = CliRunner()
        result = runner.invoke(
            cli, args, catch_exceptions=False
        )
        return result

    return _run_cli


@pytest.fixture(scope="function")
def sample_mets():
    """Well-formed sample mets"""
    return lxml.etree.parse("tests/data/mets/valid_mets.xml").getroot()


@pytest.fixture(scope="function")
def path_to_files():
    """Source path to test files"""
    return "tests/data/musicarchive/accepted_html_files"
