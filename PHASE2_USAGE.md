# Phase 2 Usage Guide: Automated Categorization

This guide provides detailed instructions for using the automated categorization tool.

## Prerequisites

1. **Completed Phase 1**: You must have output files from Phase 1 in `output/countries/`
2. **Bot Credentials**: Valid Wikimedia Commons bot account credentials
3. **Dependencies**: Installed via `pip install -r requirements.txt`

## Initial Setup

### 1. Create Bot Account

If you don't have a bot account yet:

1. Go to https://commons.wikimedia.org/wiki/Special:BotPasswords
2. Log in with your Wikimedia Commons account
3. Create a new bot password:
   - Bot name: Choose a descriptive name (e.g., "owid-categorizer")
   - Grants: Select "Edit existing pages"
   - Click "Create"
4. Save the generated username and password

### 2. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
# USERNAME should be in format: YourUsername@BotName
# PASSWORD is the generated bot password
```

Example `.env` file:
```
USERNAME=JohnDoe@owid-categorizer
PASSWORD=abcd1234efgh5678ijkl9012
```

**Important**: Never commit the `.env` file to version control!

## Running the Categorizer

### Dry-Run Mode (Recommended First Step)

Always test with dry-run mode first to see what would happen without making actual edits:

```bash
# Test on first 2 countries
python3 src/categorize_commons_files.py --dry-run --limit 2

# Test on first 5 countries
python3 src/categorize_commons_files.py --dry-run --limit 5

# Test on all countries (no edits)
python3 src/categorize_commons_files.py --dry-run
```

The dry-run output will show:
- Which files would be processed
- Which categories would be added
- Which files already have categories (skipped)

### Production Mode

After verifying with dry-run, remove the `--dry-run` flag:

```bash
# Process first 5 countries
python3 src/categorize_commons_files.py --limit 5

# Process all countries
python3 src/categorize_commons_files.py
```

## What Happens

For each country in `output/countries/*.json`:

1. **Load Data**: Reads the country's JSON file
2. **Normalize Country Name**: Applies proper English grammar (adds "the" prefix where appropriate)
3. **Connect**: Logs into Wikimedia Commons with your bot credentials
4. **Ensure Category Exists**:
   - Checks if the category page `Category:Our World in Data graphs of {NormalizedCountry}` exists
   - If not, creates it with content: `[[Category:Our World in Data graphs|{NormalizedCountry}]]`
   - Saves with edit summary: `"Create category for {NormalizedCountry} OWID graphs (automated)"`
5. **Process Graphs**: For each graph file:
   - Fetches the current page content
   - Checks if category already exists
   - If not, adds: `[[Category:Our World in Data graphs of {NormalizedCountry}]]`
   - Saves with edit summary: `"Add Category:Our World in Data graphs of {NormalizedCountry} (automated)"`
6. **Rate Limiting**: Waits 1.5 seconds between each edit
7. **Logging**: Records all actions to console and log file

## Output and Logs

### Console Output

Real-time progress is displayed on the console:
```
2025-12-07 12:00:00,000 - INFO - ================================================================================
2025-12-07 12:00:00,000 - INFO - OWID Commons File Categorizer
2025-12-07 12:00:00,000 - INFO - ================================================================================
2025-12-07 12:00:01,000 - INFO - Connecting to Wikimedia Commons...
2025-12-07 12:00:02,000 - INFO - Successfully connected and logged in
2025-12-07 12:00:03,000 - INFO - Found 150 country files
2025-12-07 12:00:04,000 - INFO - 
Processing CAN (Canada): 45 graphs
2025-12-07 12:00:05,000 - INFO - Successfully added 'Category:Our World in Data graphs of Canada' to File:...
```

### Log File

All actions are also saved to: `logs/categorize_commons.log`

This includes:
- Connection status
- Files processed
- Categories added
- Errors encountered
- Final summary statistics

## Understanding the Summary

At the end of the run, you'll see a summary:

```
================================================================================
FINAL SUMMARY
================================================================================
Countries processed: 150
Categories added: 2,450
Already had category (skipped): 320
Errors: 5
================================================================================
```

- **Countries processed**: Number of country JSON files processed
- **Categories added**: Number of files that had categories added
- **Already had category**: Files that already had the correct category
- **Errors**: Files that couldn't be processed (check logs for details)

## Troubleshooting

### "USERNAME and/or PASSWORD not found in .env file"

Solution: Create a `.env` file with your bot credentials (see Setup section)

### "Failed to connect to Wikimedia Commons"

Possible causes:
- Invalid credentials
- Network connectivity issues
- Bot account not properly configured

Solution: Verify credentials at https://commons.wikimedia.org/wiki/Special:BotPasswords

### "Countries directory not found"

Solution: Run Phase 1 first to generate the country JSON files:
```bash
python3 src/fetch_commons_files.py
# or for testing:
python3 tests/test_fetch_commons.py
```

### "Page does not exist"

This means a file mentioned in the JSON no longer exists on Commons. The script will log a warning and continue processing other files.

## Best Practices

1. **Always test first**: Use `--dry-run` before making real edits
2. **Start small**: Use `--limit` to process a few countries first
3. **Monitor logs**: Watch the console output and check log files
4. **Check edits**: Visit a few categorized files on Commons to verify
5. **Run during low-traffic hours**: Be considerate of server load
6. **Keep credentials secure**: Never share or commit your `.env` file

## Rate Limiting

The script includes a 1.5 second delay between edits to respect Wikimedia's rate limits. This means:
- ~40 edits per minute
- ~2,400 edits per hour

For large batches (thousands of files), the script may run for several hours.

## Category Format

Categories are added with proper English grammar. Country names are automatically normalized to include "the" where appropriate:

```
[[Category:Our World in Data graphs of Canada]]
[[Category:Our World in Data graphs of Brazil]]
[[Category:Our World in Data graphs of the United Kingdom]]
[[Category:Our World in Data graphs of the Philippines]]
[[Category:Our World in Data graphs of the Netherlands]]
[[Category:Our World in Data graphs of the Dominican Republic]]
[[Category:Our World in Data graphs of the United Arab Emirates]]
[[Category:Our World in Data graphs of the Democratic Republic of Congo]]
```

The category name uses the full country name from the JSON file (not the ISO3 code), with automatic normalization for countries that require "the" prefix according to English grammar rules. 

**Countries that get "the" prefix:**
- Democratic Republic of Congo
- Dominican Republic
- Philippines
- Netherlands
- United Arab Emirates
- United Kingdom

## Safety Features

- **Duplicate detection**: Won't add category if it already exists
- **Dry-run mode**: Test without making changes
- **Error recovery**: Continues processing if individual files fail
- **Comprehensive logging**: Full audit trail of all actions
- **Rate limiting**: Respects server limits automatically

## Notes

- **Only graphs are processed**: Map files are not categorized (as per design)
- **Edit summaries**: All edits include an automated edit summary
- **Reversibility**: If needed, categories can be removed manually or via another script
- **User-Agent**: Includes proper identification for Commons API

## Getting Help

If you encounter issues:

1. Check the log file: `logs/categorize_commons.log`
2. Review the error messages in console output
3. Test with dry-run mode to isolate problems
4. Verify your bot credentials are correct
5. Check the Commons bot policy: https://commons.wikimedia.org/wiki/Commons:Bots

## Example Session

Complete example workflow:

```bash
# 1. Generate test data (or run Phase 1)
python3 tests/test_fetch_commons.py

# 2. Set up credentials
cp .env.example .env
# Edit .env with your credentials

# 3. Test with dry-run
python3 src/categorize_commons_files.py --dry-run --limit 2

# 4. Review the output, then run for real
python3 src/categorize_commons_files.py --limit 2

# 5. If successful, process more countries
python3 src/categorize_commons_files.py --limit 10

# 6. Finally, process all
python3 src/categorize_commons_files.py
```
