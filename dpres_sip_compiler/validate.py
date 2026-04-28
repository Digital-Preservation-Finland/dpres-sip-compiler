"""Recursively scrape files in given path."""
import datetime
import os
import fnmatch
from file_scraper.scraper import Scraper
from file_scraper.utils import ensure_text
from dpres_sip_compiler.base_adaptor import sip_metadata_class
from dpres_sip_compiler.adaptor_list import ADAPTOR_DICT


def ignore_concealing_bitstream_errors(scraper_result: dict) -> dict:
    """
    Checks if DV files contain only concealing bitstream errors. These
    files are set to be well-formed. If any other errors exist, the
    well-formedness value is returned as it is.

    This functionality is copied from dpres-ipt, where special handling
    for concealing bitstream errors has been implemented.
    """

    cleared_previous_error = False
    other_errors_found = False

    for scraper_info in scraper_result["tool_info"].values():
        for error_string in scraper_info["errors"]:
            for error in error_string.split("\n"):
                if "Concealing bitstream errors" in error:
                    cleared_previous_error = True
                    continue
                if "Last message repeated" in error and cleared_previous_error:
                    cleared_previous_error = False
                    continue
                cleared_previous_error = False
                if error:
                    other_errors_found = True

    if not other_errors_found:
        scraper_result["well-formed"] = True

    return scraper_result["well-formed"]


def iterate_files(source_path, config):
    """
    Iterate files recursively with skipping the files that matches to pattern
    defined in adaptor.
    :source_path: Source data path
    :config: Basic configuration
    :returns: An iterator of list of files
    """
    excl_patterns = sip_metadata_class(
        ADAPTOR_DICT, config).exclude_files(config)
    if os.path.isfile(source_path):
        yield source_path
    for root, _, files in os.walk(source_path):
        for filename in files:
            exclude = False
            path = os.path.join(root, filename)
            for pattern in excl_patterns:
                if fnmatch.fnmatch(path, pattern):
                    exclude = True

            if exclude:
                continue

            yield path


def count_files(path, config):
    """Recursively counts all files in given path.

    :path: The path which is recursively processed
    :config: Basic configuration
    :returns: The total amount of files
    """
    total = 0
    for _ in iterate_files(path, config):
        total += 1

    return total


def scrape_files(path, config):
    """Loops all files recursively in given path, scrapes the metadata
    and checks the well-formedness and grading. The function yields the
    scraped metadata together with info about the scraper tools.

    :path: The path which is recursively processed
    :config: Basic configuration
    :returns: An iterator of scraped metadata
    """
    for filepath in iterate_files(path, config):

        scraper = Scraper(filepath)
        scraper.scrape(check_wellformed=True)

        results = {
            "path": str(scraper.filename),
            "filename": os.path.basename(str(scraper.filename)),
            "timestamp": datetime.datetime.now(
                datetime.timezone.utc).isoformat(),
            "MIME type": ensure_text(scraper.mimetype),
            "version": ensure_text(scraper.version),
            "metadata": scraper.streams,
            "grade": scraper.grade(),
            "well-formed": scraper.well_formed,
            "tool_info": scraper.info
        }

        # If set, ignore concealing bitstream errors in DV files
        if config.ignore_concealing_bitstream_errors:
            # Only need to check invalid DV files
            if all((results["well-formed"] is False,
                    results["MIME type"] == "video/dv")):
                results["well-formed"] = ignore_concealing_bitstream_errors(
                    results)

        yield results
