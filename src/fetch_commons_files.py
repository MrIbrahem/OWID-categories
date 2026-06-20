#!/usr/bin/env python3
"""
OWID Commons File Fetcher and Processor

This script fetches all files from Category:Uploaded_by_OWID_importer_tool on Wikimedia Commons,
classifies them as graphs or maps, extracts country codes, and generates JSON output files.

Requirements:
- Python 3.10+ (uses union type syntax: str | None)
- requests library

Usage:
    python src/fetch_commons_files.py

"""

import argparse
import logging

from main_app.logger_config import setup_logging
from main_app.main_fetch_files import fetch_files_entry
from main_app.owid_config import LOG_FILE_FETCH_COMMONS

logger = logging.getLogger(__name__)

setup_logging(
    level="INFO",
    name="main_app",
    log_file=str(LOG_FILE_FETCH_COMMONS),
    use_colorlog=False,
    overwrite=True,
    use_console=False,
)

def main():

    parser = argparse.ArgumentParser(description="Fetch ")

    # add arg load_from_json with default true
    parser.add_argument(
        "--load_from_json",
        action="store_true",
        default=True,
        help="Load from JSON file",
    )

    args = parser.parse_args()

    fetch_files_entry(
        load_from_json=args.load_from_json,
    )


if __name__ == "__main__":
    main()
