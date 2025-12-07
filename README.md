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

- **Phase 2** (planned): Automated categorization
  - Adds country-specific categories to files on Commons
  - Uses the output from Phase 1

## Requirements

- Python 3.10+
- `requests` library

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Phase 1: Fetch and Process Files

Run the main script:

```bash
python3 fetch_commons_files.py
```

This will:
1. Fetch all files from the OWID category on Wikimedia Commons
2. Classify each file as a graph or map
3. Extract country codes and metadata
4. Generate output files in the `output/` directory

### Testing with Sample Data

To test the functionality without network access:

```bash
python3 test_fetch_commons.py
```

### Example Usage

To see examples of how to use the various functions:

```bash
python3 example_usage.py
```

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

Logs are written to `logs/fetch_commons.log` and also displayed on the console.

## Country Codes

The script uses ISO 3166-1 alpha-3 country codes. The mapping between country names and codes is defined in `owid_country_codes.py`.

## Notes

- The script includes a proper User-Agent header as required by Wikimedia API guidelines
- API requests use pagination to handle large categories (tens of thousands of files)
- Files that cannot be classified or don't match any country are logged but not included in output

## License

This project is for processing OWID data on Wikimedia Commons.
