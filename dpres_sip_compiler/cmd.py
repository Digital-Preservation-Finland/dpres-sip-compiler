"""
Command line interface
"""
import json
import os
import click
from dpres_sip_compiler.config import (get_default_config_path,
                                       get_default_temp_path)
from dpres_sip_compiler.compiler import compile_sip, clean_temp_files
from dpres_sip_compiler.compiler_ng import ng_compile_sip
from dpres_sip_compiler.validate import count_files, scrape_files
from dpres_sip_compiler.config import Config


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
@click.option("--validation/--no-validation", default=True,
              help="Validation / No validation of the files during "
                   "compilation. Defaults to validation with compilation.")
def compile_command(source_path, tar_file, temp_path, config, validation):
    """
    Compile Submission Information Package.

    SOURCE-PATH: Source path of the files to be packaged.
    """
    compile_sip(source_path, tar_file, temp_path, config, validation)


@cli.command(
    name="compile-ng",
)
@click.argument('source-path',
                type=click.Path(exists=True, file_okay=False,
                                dir_okay=True))
@click.argument('descriptive-metadata-path',
                type=click.Path(exists=True, file_okay=True,
                                dir_okay=False))
@click.option("--config",
              type=click.Path(exists=True, file_okay=True,
                              dir_okay=False),
              metavar="<FILE>",
              help="Path of the configuration file. Defaults to: "
                   "%s" % get_default_config_path(),
              default=get_default_config_path())
@click.option("--tar-file",
              type=click.Path(exists=False),
              metavar="<FILE>",
              help="Target tar file for the SIP.",
              default=None)
def compile_ng_command(source_path, descriptive_metadata_path, config,
                       tar_file):
    """
    Compile Submission Information Package.

    SOURCE-PATH: Source path of the files to be packaged.

    DESCRIPTIVE-METADATA-PATH: Path to the descriptive metadata file.
    """
    ng_compile_sip(source_path, descriptive_metadata_path, config=config,
                   tar_file=tar_file)


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


# pylint: disable=too-many-arguments, too-many-locals
@cli.command(
    name="validate",
)
@click.argument("path", type=click.Path(exists=True))
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
@click.option(
    "--summary/--no-summary", default=False,
    help=("Write summary information to separate target files named "
          "<valid-output>_summary.jsonl and <invalid-output>_summary.jsonl"))
@click.option(
    "--config", "conf_file", type=click.Path(exists=True, file_okay=True,
                                             dir_okay=False),
    metavar="<FILE>",
    help="Path of the configuration file. Defaults to: "
         "%s" % get_default_config_path(),
    default=get_default_config_path())
@click.option("--stdout", is_flag=True,
              help="Print result metadata also to stdout")
def validate(path, valid_output, invalid_output, summary, conf_file, stdout):
    """
    Recursively scrape file metadata and check well-formedness in the
    given path. The scraped metadata is saved in output files as jsonl
    in the current directory.

    PATH: Path to the files to be scraped and validated.
    """
    config = Config()
    config.configure(conf_file)
    length = count_files(path, config)
    click.echo('Found %s files.' % length)
    valid_files_count = 0
    invalid_files_count = 0
    with click.progressbar(scrape_files(path, config),
                           label="Scraping files",
                           length=length) as files:
        for file_info in files:
            if stdout:
                click.echo(json.dumps(file_info, indent=4))
            if file_info['well-formed']:
                output = valid_output
                valid_files_count += 1
            else:
                output = invalid_output
                invalid_files_count += 1
            with open(output, 'a') as outfile:
                json.dump(file_info, outfile)
                outfile.write('\n')
            if summary:
                # Create summary information and write to own output
                summary_info = {
                    'path': file_info['path'],
                    'filename': file_info['filename'],
                    'timestamp': file_info['timestamp'],
                    'MIME type': file_info['MIME type'],
                    'version': file_info['version'],
                    'grade': file_info['grade'],
                    'well-formed': file_info['well-formed']
                }
                sum_output = '{}_summary{}'.format(*os.path.splitext(output))
                with open(sum_output, 'a') as outfile:
                    json.dump(summary_info, outfile)
                    outfile.write('\n')

    click.echo('Validation finished!')
    click.echo(
        '%s files were valid. %s files were invalid or '
        'unsupported.' % (valid_files_count, invalid_files_count))


if __name__ == "__main__":
    cli()
