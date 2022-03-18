"""Common fuctions and fixtures for tests.
"""
import os
from click.testing import CliRunner
import pytest
from dpres_sip_compiler.config import Config
from dpres_sip_compiler.cmd import cli


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
