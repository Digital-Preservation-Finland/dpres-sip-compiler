"""Recursively scrape files in given path."""
import datetime
import os
from file_scraper.scraper import Scraper
from file_scraper.utils import ensure_text


def count_files(path):
    """Recursively counts all files in given path.

    :path: The path which is recursively processed
    :returns: The total amount of files
    """
    total = 0
    for _, _, files in os.walk(path):
        total += len(files)

    return total


def scrape_files(path):
    """Loops all files recursively in given path, scrapes the metadata
    and checks the well-formedness and grading. The function yields the
    scraped metadata together with info about the scraper tools.

    :path: The path which is recursively processed
    :returns: An iterator of scraped metadata
    """
    for root, _, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)

            scraper = Scraper(filepath)
            scraper.scrape(check_wellformed=True)

            results = {
                "path": ensure_text(scraper.filename),
                "filename": ensure_text(os.path.basename(scraper.filename)),
                "timestamp": datetime.datetime.now().isoformat(),
                "MIME type": ensure_text(scraper.mimetype),
                "version": ensure_text(scraper.version),
                "metadata": scraper.streams,
                "grade": scraper.grade(),
                "well-formed": scraper.well_formed,
                "tool_info": scraper.info
            }

            yield results
