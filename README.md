# OWID Commons Processing Tools

This repository contains Python scripts for processing Our World in Data (OWID) files from Wikimedia Commons.

## Overview

The tools fetch, classify, and organize OWID visualizations (graphs and maps) from Wikimedia Commons by country, generating structured JSON output files.

## Features

- **Phase 1**: Fetch and classify OWID files from Commons
  - Fetches all files from `Category:Uploaded_by_OWID_importer_tool`
  - Classifies files as graphs (time series) or maps (spatial visualizations)
  - Extracts country ISO3 codes
  - Generates JSON output per country and a global summary

- **Phase 2**: Automated categorization
  - Adds country-specific categories to graph files on Commons
  - Uses the output from Phase 1
  - Includes dry-run mode for safe testing
  - Respects Wikimedia rate limits with configurable delays

## Requirements

- Python 3.10+
- `requests` library
- `mwclient` library (for Phase 2)
- `python-dotenv` library (for Phase 2)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure

```
OWID-categories/
├── src/                             # Main source code
│   ├── categorize/
│   │   ├── wiki.py
│   │   ├── utils.py
│   │   └── __init__.py
│   ├── fetch_commons_files.py       # Phase 1: Fetch and classify files
│   ├── owid_country_codes.py        # Country code mappings
│   ├── run_countries.py             # Phase 2: Add categories
├── tests/                           # Test files
│   ├── test_fetch_commons.py        # Test suite for Phase 1
│   ├── test_categorize.py           # Test suite for Phase 2
│   └── example_usage.py             # Usage examples
├── output/                          # Generated output (gitignored)
│   ├── countries/                   # Per-country JSON files
│   └── owid_country_summary.json
├── logs/                            # Log files (gitignored)
├── .env.example                     # Example environment file
└── requirements.txt                 # Python dependencies
```

## Usage

### Phase 1: Fetch and Process Files

Run the main script:

```bash
python3 src/fetch_commons_files.py
```

This will:
1. Fetch all files from the OWID category on Wikimedia Commons
2. Classify each file as a graph or map
3. Extract country codes and metadata
4. Generate output files in the `output/` directory

### Testing with Sample Data

To test the functionality without network access:

```bash
python3 tests/test_fetch_commons.py
```

### Example Usage

To see examples of how to use the various functions:

```bash
python3 tests/example_usage.py
```

### Phase 2: Automated Categorization

Phase 2 adds country-specific categories to graph files on Wikimedia Commons.

#### Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your Wikimedia Commons bot credentials:**
   ```
   WM_USERNAME=YourBotUsername
   PASSWORD=YourBotPassword
   ```

   To create bot credentials:
   - Go to https://commons.wikimedia.org/wiki/Special:BotPasswords
   - Create a new bot password with "Edit existing pages" permission
   - Use the generated credentials in your `.env` file

3. **Ensure Phase 1 output exists:**
   ```bash
   # Either run Phase 1 to generate real data:
   python3 src/fetch_commons_files.py

   # Or generate test data:
   python3 tests/test_fetch_commons.py
   ```

#### Running the Categorizer

**Test with dry-run mode first (recommended):**
```bash
# Test on first 2 countries without making actual edits
python3 src/run_countries.py --dry-run --limit 2

# Test with just 1 file per country
python3 src/run_countries.py --dry-run --files-per-item 1

# Test on 2 countries, 1 file each
python3 src/run_countries.py --dry-run --limit 2 --files-per-item 1
```

**Run on limited set of countries:**
```bash
# Process first 5 countries
python3 src/run_countries.py --limit 5

# Process first 5 countries, 2 files per country
python3 src/run_countries.py --limit 5 --files-per-item 2
```

**Run on all countries:**
```bash
# Process all countries, all files
python3 src/run_countries.py

# Process all countries, but only 1 file per country (conservative approach)
python3 src/run_countries.py --files-per-item 1
```

**Available options:**
- `--dry-run`: Test mode without making actual edits
- `--limit N`: Process only first N countries
- `--files-per-item N`: Process only N files per country

#### What it Does

For each country's graph files, the script:
1. Loads the country JSON file from `output/countries/`
2. Connects to Wikimedia Commons using your bot credentials
3. Ensures the category page exists:
   - Checks if `Category:Our World in Data graphs of {Country}` exists
   - If not, creates it with content: `[[Category:Our World in Data graphs by country|{Country}]]`
   - Saves with edit summary: `"Create category for {Country} OWID graphs (automated)"`
4. For each graph file:
   - Checks if the country category already exists on the page
   - If not, adds: `[[Category:Our World in Data graphs of {Country}]]`
   - Saves with edit summary: `"Add Category:Our World in Data graphs of {Country} (automated)"`
5. Respects rate limits with 1.5 second delays between edits
6. Logs all actions to console and `logs/categorize_commons.log`

#### Testing

Test the categorization logic without Commons credentials:
```bash
python3 tests/test_categorize.py
```

#### Category Format

Categories are added in this format with proper English grammar:
- Canada: `Category:Our World in Data graphs of Canada`
- Brazil: `Category:Our World in Data graphs of Brazil`
- United Kingdom: `Category:Our World in Data graphs of the United Kingdom`
- United States: `Category:Our World in Data graphs of the United States`
- Philippines: `Category:Our World in Data graphs of the Philippines`
- Netherlands: `Category:Our World in Data graphs of the Netherlands`
- Dominican Republic: `Category:Our World in Data graphs of the Dominican Republic`

**Note:** Certain countries require "the" prefix according to proper English grammar rules. The script automatically normalizes country names to include "the" for: **Democratic Republic of Congo**, **Dominican Republic**, **Philippines**, **Netherlands**, **United Arab Emirates**, **United Kingdom**, **United States**, **Czech Republic**, **Central African Republic**, **Maldives**, **Seychelles**, **Bahamas**, **Marshall Islands**, **Solomon Islands**, **Comoros**, **Gambia**, and **Vatican City**.

#### Safety Features

- **Dry-run mode**: Test without making actual edits
- **Limit option**: Process only a subset of countries for testing
- **Duplicate detection**: Skips files that already have the category
- **Rate limiting**: 1.5 second delay between edits
- **Comprehensive logging**: All actions logged to file and console
- **Error handling**: Continues processing if individual files fail

### Output Structure

```
output/
├── countries/
│   ├── CAN.json    # Canadian graphs and maps
│   ├── BRA.json    # Brazilian graphs and maps
│   └── ...
└── owid_country_summary.json  # Global summary with statistics
```

#### Country JSON Format

Each country file contains:

```json
{
  "iso3": "CAN",
  "country": "Canada",
  "graphs": [
    {
      "title": "File:Agriculture share gdp, 1997 to 2021, CAN.svg",
      "indicator": "Agriculture share gdp",
      "start_year": 1997,
      "end_year": 2021,
      "file_page": "https://commons.wikimedia.org/wiki/File:Agriculture_share_gdp,_1997_to_2021,_CAN.svg"
    }
  ],
  "maps": [
    {
      "title": "File:Access to clean fuels and technologies for cooking, Canada, 1990.svg",
      "indicator": "Access to clean fuels and technologies for cooking",
      "year": 1990,
      "region": "Canada",
      "file_page": "https://commons.wikimedia.org/wiki/File:Access_to_clean_fuels_and_technologies_for_cooking,_Canada,_1990.svg"
    }
  ]
}
```

#### Summary JSON Format

The summary file contains statistics for all countries:

```json
[
  {
    "iso3": "CAN",
    "country": "Canada",
    "graph_count": 123,
    "map_count": 45
  }
]
```

## File Classification

### Graphs (Time Series)

Files matching this pattern are classified as graphs:
- Pattern: `<indicator>, <start_year> to <end_year>, <ISO3>.svg`
- Example: `Agriculture share gdp, 1997 to 2021, CAN.svg`

### Maps (Spatial Visualizations)

Files matching this pattern are classified as maps:
- Pattern: `<indicator>, <region_or_country>, <year>.svg`
- Example: `Access to clean fuels and technologies for cooking, Canada, 1990.svg`

## Logging

- Phase 1 logs: `logs/fetch_commons.log`
- Phase 2 logs: `logs/categorize_commons.log`

All logs are also displayed on the console in real-time.

## Country Codes

The script uses ISO 3166-1 alpha-3 country codes. The mapping between country names and codes is defined in `src/owid_country_codes.py`.

## Notes

- The script includes a proper User-Agent header as required by Wikimedia API guidelines
- API requests use pagination to handle large categories (tens of thousands of files)
- Files that cannot be classified or don't match any country are logged but not included in output

## License

This project is for processing OWID data on Wikimedia Commons.
