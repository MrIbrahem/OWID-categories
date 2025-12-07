# Copilot Instructions for OWID-categories

## Project Overview

This repository contains tools for processing and categorizing Our World in Data (OWID) files from Wikimedia Commons. The project consists of two main phases:

1. **Phase 1**: Fetch and classify files from Commons, extracting country codes and generating JSON outputs
2. **Phase 2**: Automatically add appropriate categories to graph files on Wikimedia Commons

## Project Structure

- `plan.md` - Detailed implementation plan for Phase 1 (fetching and classifying files)
- `plan2.md` - Implementation plan for Phase 2 (automated categorization)
- `output/` - Generated JSON files (per-country and summary data)
- `output/countries/` - Individual country JSON files (e.g., `CAN.json`, `BRA.json`)

## Technology Stack

### Primary Language
- **Python 3.10+**

### Core Dependencies
- `requests` - HTTP requests to MediaWiki API
- `mwclient` - MediaWiki API client for automated edits
- `python-dotenv` - Environment variable management
- Standard library: `json`, `re`, `pathlib`, `logging`, `typing`

## Coding Standards

### Python Style
- Follow **PEP 8** style guidelines
- Use type hints for function parameters and return values
- Include docstrings for all functions, classes, and modules
- Use descriptive variable names (e.g., `iso3_code` not `c`)

### File Naming Patterns

The project processes two types of files:

**Graph files** (time series):
```
<indicator>, <start_year> to <end_year>, <ISO3>.svg
Example: Agriculture share gdp, 1997 to 2021, CAN.svg
```

**Map files** (spatial visualization):
```
<indicator>, <region_or_country>, <year>.svg
Example: Access to clean fuels and technologies for cooking, Canada, 1990.svg
```

### Regular Expressions
- **Graph pattern**: `,\s*(\d{4})\s+to\s+(\d{4}),\s*([A-Z]{3})\.svg$`
- **Map pattern**: `,\s*([A-Za-z \-\(\)]+),\s*(\d{4})\.svg$`

## Best Practices

### API Interactions
1. **Always include User-Agent headers** in MediaWiki API requests
   - Format: `OWID-Commons-Processor/1.0 (contact: email@example.com)`
   - Requests without User-Agent may be throttled or blocked
   
2. **Handle pagination properly**
   - Use `cmcontinue` for category member pagination
   - Process responses in batches
   - Log progress for large datasets

3. **Respect rate limits**
   - Add delays between API requests (1-2 seconds)
   - Implement exponential backoff for retries
   - Never make concurrent requests without proper throttling

### Error Handling
- Wrap API calls in try/except blocks
- Log warnings for unclassified files
- Continue processing on individual file failures
- Create comprehensive error logs

### Data Management
- Store sensitive credentials in `.env` files (never commit)
- Use `.gitignore` for environment files
- Validate ISO3 codes against OWID country code dictionary
- Maintain data consistency across JSON outputs

### Security
- Never commit credentials or API keys
- Use secure authentication methods (OAuth when available)
- Validate and sanitize all external data
- Follow Wikimedia's bot policy and guidelines

## Testing Approach
- Implement dry-run modes before making live edits
- Spot-check output files manually
- Validate JSON structure and content
- Test with a small subset of files first
- Cross-check counts and statistics

## Logging
- Use Python's `logging` module
- Log levels:
  - **INFO**: Normal progress, batch completions
  - **WARNING**: Unclassified files, missing country codes
  - **ERROR**: API failures, authentication issues
- Include timestamps and context in log messages
- Save logs to `logs/` directory

## Output Format

### Per-Country JSON (`output/countries/{ISO3}.json`)
```json
{
  "iso3": "CAN",
  "country": "Canada",
  "graphs": [
    {
      "title": "File:...",
      "indicator": "...",
      "start_year": 1997,
      "end_year": 2021,
      "file_page": "https://commons.wikimedia.org/wiki/File:..."
    }
  ],
  "maps": [
    {
      "title": "File:...",
      "indicator": "...",
      "year": 1990,
      "region": "Canada",
      "file_page": "https://commons.wikimedia.org/wiki/File:..."
    }
  ]
}
```

### Global Summary (`output/owid_country_summary.json`)
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

## Important Notes

1. **Country Code Mapping**: Use the `OWID_COUNTRY_CODES` dictionary for all country name ↔ ISO3 conversions
2. **File Classification**: If a file doesn't match graph or map patterns, log it as "unknown" - don't force classification
3. **Regional Files**: Files for regions (e.g., "Africa", "Asia") without specific ISO3 codes should be handled separately
4. **MediaWiki Conventions**: File titles on Commons use underscores in URLs but spaces in display names
5. **UTF-8 Encoding**: Always use UTF-8 for reading/writing JSON files

## Future Extensions
- CSV export functionality
- Per-indicator statistics
- Regional JSON support for continent-level data
- Integration with Pywikibot for advanced categorization
- Automated verification and validation tools

## When Working on This Repository
- Read the relevant plan document (`plan.md` or `plan2.md`) first
- Follow the step-by-step implementation order
- Test with small datasets before full runs
- Document any deviations from the plan
- Update this file if you discover new conventions or best practices
