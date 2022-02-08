"""Common fuctions and fixtures for tests.
"""
import os
from shutil import copytree
from click.testing import CliRunner
import pytest
from dpres_sip_compiler.config import Config
from dpres_sip_compiler.cmd import cli


@pytest.fixture(scope="function")
def prepare_workspace():
    """
    Prepare temporary workspace.
    """
    def _prepare(tmp_path, workspace="workspace2"):
        """
        Prepare temporary workspace.
        :tmp_path: Temporary test path
        :workspace: Workspace case from test data
        :returns: Workspace with path and configuration
        """
        destination = os.path.join(str(tmp_path), workspace)
        copytree(os.path.join("tests/data/musicarchive", workspace), destination)
        config = Config()
        config.configure("tests/data/musicarchive/config.conf")
        return (destination, config)

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
