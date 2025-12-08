
import os
from dotenv import load_dotenv
from pathlib import Path

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
