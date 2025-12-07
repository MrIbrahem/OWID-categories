# OWID Categories - Quick Start Guide

This is a quick reference for running the OWID Commons processing tools.

## Phase 1: Fetch and Classify Files

Fetch all OWID files from Wikimedia Commons and classify them:

```powershell
python src/fetch_commons_files.py
```

**Output:**
- `output/countries/*.json` - Per-country data files
- `output/continents/*.json` - Per-continent data files
- `output/owid_country_summary.json` - Global summary
- `output/not_matched_files.txt` - Files that couldn't be classified
- `output/fetch_commons.log` - Processing log

---

## Phase 2: Add Categories to Commons

Add country-specific categories to graph files on Wikimedia Commons.

### Prerequisites
1. Complete Phase 1 first
2. Create a `.env` file with bot credentials:
   ```
   WM_USERNAME=YourBotUsername@BotName
   PASSWORD=YourBotPassword
   ```

### Testing (Dry-Run)

**Always test with dry-run first!**

```powershell
# Test with 2 countries only
python src/categorize_commons_files.py --dry-run --limit 2

# Test with 1 file per country
python src/categorize_commons_files.py --dry-run --files-per-country 1

# Test with 2 countries, 1 file each
python src/categorize_commons_files.py --dry-run --limit 2 --files-per-country 1
```

### Production Run

```powershell
# Process first 5 countries
python src/categorize_commons_files.py --limit 5

# Process first 10 countries, 2 files per country
python src/categorize_commons_files.py --limit 10 --files-per-country 2

# Process all countries, 1 file per country (conservative)
python src/categorize_commons_files.py --files-per-country 1

# Process all countries, all files
python src/categorize_commons_files.py
```

---

## Command-Line Options

### Phase 2 Options

| Option | Description | Example |
|--------|-------------|---------|
| `--dry-run` | Test mode without making actual edits | `--dry-run` |
| `--limit N` | Process only first N countries | `--limit 5` |
| `--files-per-country N` | Process only N files per country | `--files-per-country 1` |

### Combining Options

All options can be combined for fine-grained control:

```powershell
# Test: 3 countries, 2 files each
python src/categorize_commons_files.py --dry-run --limit 3 --files-per-country 2
```

---

## Common Workflows

### 1. Initial Setup and Test
```powershell
# 1. Fetch all files from Commons
python src/fetch_commons_files.py

# 2. Dry-run test with minimal data
python src/categorize_commons_files.py --dry-run --limit 1 --files-per-country 1

# 3. Check the log output
type logs\categorize_commons.log
```

### 2. Conservative Production Run
```powershell
# Process 1 file per country to verify everything works
python src/categorize_commons_files.py --files-per-country 1

# If successful, process remaining files
python src/categorize_commons_files.py
```

### 3. Batch Processing
```powershell
# Process countries in batches of 10
python src/categorize_commons_files.py --limit 10
# ... check results ...
# Modify JSON files to mark processed countries, then continue
```

---

## Logs and Output

### Log Files
- **Phase 1:** `output/fetch_commons.log`
- **Phase 2:** `logs/categorize_commons.log`

### View Logs
```powershell
# View last 50 lines of Phase 2 log
Get-Content logs\categorize_commons.log -Tail 50

# Follow log in real-time
Get-Content logs\categorize_commons.log -Wait -Tail 20
```

---

## Troubleshooting

### "Countries directory not found"
Run Phase 1 first: `python src/fetch_commons_files.py`

### "WM_USERNAME and/or PASSWORD not found"
Create a `.env` file with your bot credentials (see Prerequisites above)

### "Failed to connect to Wikimedia Commons"
- Check your internet connection
- Verify credentials in `.env` file
- Ensure bot account has proper permissions

### "Rate limit exceeded"
The script includes built-in rate limiting (1.5s between edits). If you still hit limits:
- Reduce the number of countries: `--limit 5`
- Reduce files per country: `--files-per-country 1`
- Wait a few minutes and resume

---

## Best Practices

1. ✅ **Always test with `--dry-run` first**
2. ✅ **Start small with `--limit` and `--files-per-country`**
3. ✅ **Monitor logs during execution**
4. ✅ **Verify edits on Commons after small batches**
5. ✅ **Never commit your `.env` file**
6. ✅ **Run during low-traffic hours**
7. ✅ **Keep backups of JSON files**

---

## Quick Reference

```powershell
# Phase 1: Fetch everything
python src/fetch_commons_files.py

# Phase 2: Safe testing
python src/categorize_commons_files.py --dry-run --limit 2 --files-per-country 1

# Phase 2: Conservative real run
python src/categorize_commons_files.py --limit 5 --files-per-country 1

# Phase 2: Full run
python src/categorize_commons_files.py
```

---

For detailed documentation, see:
- **README.md** - Project overview
- **PHASE2_USAGE.md** - Comprehensive Phase 2 guide
- **CONTRIBUTING.md** - Developer documentation
