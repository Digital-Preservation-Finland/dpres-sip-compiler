"""Recursively scrape files in given path."""
import os
from file_scraper.scraper import Scraper
from file_scraper.utils import ensure_text


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
                "MIME type": ensure_text(scraper.mimetype),
                "version": ensure_text(scraper.version),
                "metadata": scraper.streams,
                "grade": scraper.grade(),
                "well-formed": scraper.well_formed,
                "tool_info": scraper.info
            }

            yield results
