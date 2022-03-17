"""
Command line interface
"""
import click
from dpres_sip_compiler.config import get_default_config_path
from dpres_sip_compiler.compiler import compile_sip, clean_temp_files


@click.group()
def cli():
    """SIP Compiler"""


@cli.command(
    name="compile",
)
@click.argument('workspace', type=click.Path(exists=True))
@click.option(
    "--config", type=click.Path(exists=True), metavar="<PATH>",
    help="Path of the configuration file. Defaults to: "
         "%s" % get_default_config_path(),
    default=get_default_config_path())
def compile_command(config, workspace):
    """
    Compile Submission Information Package.

    WORKSPACE: Workspace path.
    """
    compile_sip(workspace, config)


@cli.command(
    name="clean",
    help="Clean workspace"
)
@click.argument('workspace', type=click.Path(exists=True))
def clean_command(workspace):
    """
    Clean workspace from temporary files.

    WORKSPACE: Workspace path.
    """
    clean_temp_files(workspace)


if __name__ == "__main__":
    cli()
