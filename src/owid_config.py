
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

load_dotenv()

MAIN_DIR = Path()

if os.getenv("MAIN_DIR", ""):
    MAIN_DIR = Path(os.getenv("MAIN_DIR"))

WM_USERNAME = os.getenv("WM_USERNAME")
PASSWORD = os.getenv("PASSWORD")

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
    username = os.getenv("WM_USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        logging.error("WM_USERNAME and/or PASSWORD not found in .env file")
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
]
