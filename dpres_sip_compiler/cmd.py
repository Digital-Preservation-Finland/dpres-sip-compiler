"""
Command line interface
"""
import json
import os

import click
from dpres_sip_compiler.config import get_default_config_path
from dpres_sip_compiler.compiler import compile_sip
from dpres_sip_compiler.validate import count_files, scrape_files
from dpres_sip_compiler.config import Config


@click.group()
def cli():
    """SIP Compiler"""


@cli.command(
    name="compile",
)
@click.argument('source-path',
                type=click.Path(exists=True, file_okay=False,
                                dir_okay=True))
@click.argument('descriptive-metadata-path',
                type=click.Path(exists=True, file_okay=True,
                                dir_okay=False),
                required=False,
                nargs=-1)
@click.option("--tar-file",
              type=click.Path(exists=False),
              metavar="<FILE>",
              help="Target tar file for the SIP. Defaults to sip.tar",
              default="sip.tar")
@click.option("--config",
              type=click.Path(exists=True, file_okay=True,
                              dir_okay=False),
              metavar="<FILE>",
              help="Path of the configuration file. Defaults to: "
                   "%s" % get_default_config_path(),
              default=get_default_config_path())
@click.option("--validation/--no-validation", default=True,
              help="Validation / No validation of the files during "
                   "compilation. Defaults to validation with compilation.")
def compile_command(source_path, descriptive_metadata_path, tar_file,
                    config, validation):
    """
    Compile Submission Information Package.

    SOURCE-PATH: Source path of the files to be packaged.

    DESCRIPTIVE-METADATA-PATH: Zero or more file paths to descriptive metadata.
    """
    compile_sip(source_path,
                tar_file,
                descriptive_metadata_paths=list(descriptive_metadata_path),
                conf_file=config,
                validation=validation)


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
    Recursively validate files in given path.

    PATH: Root path to be scanned.
    """
    config = Config(conf_file=conf_file)

    click.echo('Starting file validation...')
    click.echo('Total number of files: %d.' % count_files(path, config))

    invalid_files_count = 0
    valid_files_count = 0

    for file_info in scrape_files(path, config):
        if stdout:
            click.echo(json.dumps(file_info))

        if file_info['well-formed'] and file_info['grade'] != 'unacceptable':
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
