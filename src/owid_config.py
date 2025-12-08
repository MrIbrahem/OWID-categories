
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

OUTPUT_DIR = Path("output")
LOG_DIR = Path("logs")

LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

COUNTRIES_DIR = OUTPUT_DIR / "countries"
CONTINENTS_DIR = OUTPUT_DIR / "continents"

LOG_FILE_COUNTRIES = LOG_DIR / "categorize_countries.log"
LOG_FILE_CONTINENTS = LOG_DIR / "categorize_continents.log"
