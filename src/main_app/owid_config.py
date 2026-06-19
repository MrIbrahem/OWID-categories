#!/usr/bin/env python3
"""
OWID Configuration Module

Centralized configuration for OWID Commons categorization scripts.
Defines output directories, log file paths, and loads environment variables.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")

main_dir = os.getenv("MAIN_DIR", "")
MAIN_DIR = Path(main_dir) if main_dir else Path()

WIKIPEDIA_BOT_USERNAME = os.getenv("WIKIPEDIA_BOT_USERNAME")
WIKIPEDIA_BOT_PASSWORD = os.getenv("WIKIPEDIA_BOT_PASSWORD")

LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", "WARNING")

OUTPUT_DIR = MAIN_DIR / "output"
LOG_DIR = MAIN_DIR / "logs"

# Ensure log directory exists
LOG_DIR.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.parent.mkdir(parents=True, exist_ok=True)

COUNTRIES_DIR = OUTPUT_DIR / "countries"
CONTINENTS_DIR = OUTPUT_DIR / "continents"

LOG_FILE_COUNTRIES = LOG_DIR / "categorize_countries.log"
LOG_FILE_CONTINENTS = LOG_DIR / "categorize_continents.log"


def load_credentials() -> tuple[Optional[str], Optional[str]]:
    """
    Load credentials from .env file.

    Returns:
        Tuple of (username, password) or (None, None) if not found
    """
    username = os.getenv("WIKIPEDIA_BOT_USERNAME")
    password = os.getenv("WIKIPEDIA_BOT_PASSWORD")

    if not username or not password:
        logger.error("WIKIPEDIA_BOT_USERNAME and/or WIKIPEDIA_BOT_PASSWORD not found in .env file")
        return None, None

    return username, password


__all__ = [
    "load_credentials",
    "OUTPUT_DIR",
    "LOG_DIR",
    "COUNTRIES_DIR",
    "CONTINENTS_DIR",
    "LOG_FILE_COUNTRIES",
    "LOG_FILE_CONTINENTS",
    "LOGGER_LEVEL",
]
