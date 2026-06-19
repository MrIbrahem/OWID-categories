#!/usr/bin/env python3
"""
OWID Commons File Fetcher and Processor

This script fetches all files from Category:Uploaded_by_OWID_importer_tool on Wikimedia Commons,
classifies them as graphs or maps, extracts country codes, and generates JSON output files.

Requirements:
- Python 3.10+ (uses union type syntax: str | None)
- requests library
"""

import logging

from main_app.main_fetch_files import fetch_files_entry
from main_app.owid_config import LOG_FILE_COUNTRIES
from main_app.logger_config import setup_logging

logger = logging.getLogger(__name__)

setup_logging(
    level="INFO",
    name="main_app",
    log_file=str(LOG_FILE_COUNTRIES),
    use_colorlog=False,
    overwrite=True,
)
if __name__ == "__main__":
    fetch_files_entry()
