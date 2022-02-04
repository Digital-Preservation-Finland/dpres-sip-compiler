"""
Command line interface
"""
import click
from dpres_sip_compiler.compiler import compile_sip, clean_workspace


@click.group()
def cli():
    """SIP Compiler"""


@cli.command(
    name="compile",
    help="Compile Submission Information Package"
)
@click.argument('config', type=click.Path(exists=True))
@click.argument('workspace', type=click.Path(exists=True))
@click.pass_context
def compile_command(config, workspace):
    """
    Compile Submission Information Package.

    \b
    CONFIG: Configuration file.
    WORKSPACE: Workspace path.
    """
    compile_sip(config, workspace)


@cli.command(
    name="clean",
    help="Clean workspace"
)
@click.argument('workspace', type=click.Path(exists=True))
@click.pass_context
def clean_command(workspace):
    """
    Clean workspace from temporary files.

    WORKSPACE: Workspace path.
    """
    clean_workspace(workspace)


if __name__ == "__main__":
    cli()
