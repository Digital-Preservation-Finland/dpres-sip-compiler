"""
Command line interface
"""
import json
import os
import click
from dpres_sip_compiler.config import (get_default_config_path,
                                       get_default_temp_path)
from dpres_sip_compiler.compiler import compile_sip, clean_temp_files
from dpres_sip_compiler.validate import count_files, scrape_files


@click.group()
def cli():
    """SIP Compiler"""


@cli.command(
    name="compile",
)
@click.argument('source-path', type=click.Path(exists=True, file_okay=False,
                                               dir_okay=True))
@click.option(
    "--tar-file", type=click.Path(exists=False), metavar="<FILE>",
    help="Target tar file for the SIP. Defaults to: "
         "%s/<trimmed-objid>.tar" % os.getcwd(), default=None)
@click.option(
    "--temp-path", type=click.Path(dir_okay=True, writable=True),
    metavar="<DIR>",
    help="Path of temporary files. Defaults to e.g.: "
         "%s/<timestamp>" % os.getcwd(),
    default=get_default_temp_path())
@click.option(
    "--config", type=click.Path(exists=True, file_okay=True,
                                dir_okay=False),
    metavar="<FILE>",
    help="Path of the configuration file. Defaults to: "
         "%s" % get_default_config_path(),
    default=get_default_config_path())
def compile_command(source_path, tar_file, temp_path, config):
    """
    Compile Submission Information Package.

    SOURCE-PATH: Source path of the files to be packaged.
    """
    compile_sip(source_path, tar_file, temp_path, config)


@cli.command(
    name="clean",
)
@click.argument('temp-path', type=click.Path(exists=True))
@click.option("--delete-path", is_flag=True,
              help="Flag to delete the directory of temporary files. "
                   "Removed only if it is empty after cleaning.")
def clean_command(temp_path, delete_path):
    """
    Clean directory from temporary files.

    DIRECTORY: Directory containing temporary files.
    """
    clean_temp_files(temp_path, delete_path=delete_path)


@cli.command(
    name="validate",
)
@click.argument('path', type=click.Path(exists=True))
@click.option(
    "--valid-output", type=click.Path(exists=False), metavar="<FILE>",
    help=("Target file to write result metadata for valid and supported "
          "files. Defaults to: ./validate_files_valid.jsonl"),
    default="./validate_files_valid.jsonl")
@click.option(
    "--invalid-output", type=click.Path(exists=False), metavar="<FILE>",
    help=("Target file to write result metadata for invalid or unsupported "
          "files. Defaults to: ./validate_files_invalid.jsonl"),
    default="./validate_files_invalid.jsonl")
@click.option('--stdout', is_flag=True,
              help='Print result metadata also to stdout')
def validate(path, valid_output, invalid_output, stdout):
    """
    Recursively scrape file metadata and check well-formedness in the
    given path. The scraped metadata is saved in output files as jsonl
    in the current directory.

    PATH: Path to the files to be scraped and validated.
    """
    length = count_files(path)
    click.echo('Found %s files.' % length)
    with click.progressbar(scrape_files(path),
                           label="Scraping files",
                           length=length) as files:
        for file_info in files:
            if stdout:
                click.echo(json.dumps(file_info, indent=4))
            out = valid_output if file_info['well-formed'] else invalid_output
            with open(out, 'at', encoding='utf-8') as outfile:
                json.dump(file_info, outfile)
                outfile.write('\n')


if __name__ == "__main__":
    cli()
