# Contributing to OWID Commons Processing

This document provides technical details for developers contributing to the project.

## Project Structure

```
OWID-categories/
├── src/                        # Main source code
│   ├── categorize/
│   │   ├── wiki.py
│   │   ├── utils.py
│   │   └── __init__.py
│   ├── run_countries.py
│   ├── fetch_commons_files.py  # Main script for fetching and processing
│   └── owid_country_codes.py   # Country code mappings and lookup functions
├── tests/                      # Test files
│   ├── test_fetch_commons.py   # Test suite with sample data
│   └── example_usage.py        # Usage examples and demonstrations
├── requirements.txt            # Python dependencies
├── README.md                   # User-facing documentation
├── CONTRIBUTING.md             # Developer documentation
├── plans/                      # Plans files
│   ├── plan.md                 # Phase 1 implementation plan
│   └── plan2.md                # Phase 2 implementation plan
├── .gitignore                  # Git exclusions
├── output/                     # Generated JSON files (gitignored)
│   ├── countries/              # Per-country JSON files
│   │   ├── CAN.json
│   │   ├── USA.json
│   │   └── ...
│   └── owid_country_summary.json
└── logs/                       # Log files (gitignored)
    └── fetch_commons.log
```

## Core Components

### 1. Country Code Mappings (`src/owid_country_codes.py`)

Provides:
- `OWID_COUNTRY_CODES`: Dictionary mapping country names to ISO3 codes
- `ISO3_TO_COUNTRY`: Reverse mapping for O(1) lookups
- `get_iso3_from_country(country_name)`: Lookup function
- `get_country_from_iso3(iso3)`: Reverse lookup function

### 2. Main Processing Script (`src/fetch_commons_files.py`)

Key functions:

#### API Integration
- `fetch_category_members()`: Fetches all files from Commons with pagination
  - Handles cmcontinue tokens for large categories
  - Includes proper User-Agent header
  - Returns list of file dictionaries

#### File Classification
- `classify_and_parse_file(title)`: Parses filename and extracts metadata
  - Returns `(file_type, parsed_data)` tuple
  - `file_type` is "graph", "map", or None
  - Uses regex patterns for classification

#### Data Processing
- `fetch_files(files)`: Aggregates files by country
  - Classifies each file
  - Resolves country codes
  - Builds in-memory data structure
  - Returns country dictionary

#### Output Generation
- `write_country_json_files(countries)`: Writes per-country JSON files
- `write_summary_json(countries)`: Writes global summary

### 3. Testing (`tests/test_fetch_commons.py`)

- Uses sample data to test functionality
- No network access required
- Validates classification and output generation

### 4. Examples (`tests/example_usage.py`)

- Demonstrates all major functions
- Shows how to read output files
- Useful for learning the API

## Regex Patterns

### Graph Pattern
```python
GRAPH_PATTERN = r",\s*(\d{4})\s+to\s+(\d{4}),\s*([A-Z]{3})\.svg$"
```

Matches: `Agriculture share gdp, 1997 to 2021, CAN.svg`
- Captures: start_year, end_year, iso3

### Map Pattern
```python
MAP_PATTERN = r",\s*([A-Z][A-Za-z \-\(\)]+),\s*(\d{4})\.svg$"
```

Matches: `Life expectancy, Canada, 2020.svg`
- Captures: region, year
- Region must start with capital letter

## Data Flow

1. **Fetch**: API call → list of file titles
2. **Classify**: Regex matching → file_type + metadata
3. **Resolve**: Country name → ISO3 code
4. **Aggregate**: Group by ISO3 → country data structure
5. **Output**: Write JSON files

## Adding New Features

### Adding a New File Type

1. Add regex pattern to `src/fetch_commons_files.py`
2. Update `classify_and_parse_file()` to handle new pattern
3. Update `fetch_files()` to handle new file type
4. Update output JSON structure in `write_country_json_files()`
5. Add tests in `tests/test_fetch_commons.py`

### Adding New Country Codes

1. Update `OWID_COUNTRY_CODES` dictionary in `src/owid_country_codes.py`
2. The reverse mapping `ISO3_TO_COUNTRY` is generated automatically
3. Test with sample files

## Error Handling

The script handles:
- Network errors (with logging)
- Files that don't match patterns (logged as "unknown")
- Regions that can't resolve to countries (logged as "unresolved")
- Missing or invalid data (validation checks)

## Performance Considerations

- **Country lookup**: O(1) using reverse mapping dictionary
- **File classification**: O(n) where n = number of files
- **Output writing**: O(m) where m = number of countries
- **Memory usage**: All files kept in memory (acceptable for <100k files)

## Testing

```bash
# Run tests with sample data
python3 tests/test_fetch_commons.py

# Run examples
python3 tests/example_usage.py

# Run main script (requires network access)
python3 src/fetch_commons_files.py
```

## Code Style

- Python 3.10+ type hints
- Docstrings for all functions
- Descriptive variable names
- Logging for important events
- Comments for complex logic

## Future Work

See `plan2.md` for Phase 2 implementation plan:
- Automated categorization using `mwclient`
- Adding country-specific categories to Commons files
- Batch editing with rate limiting
