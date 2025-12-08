# OWID Configuration Guide (`owid_config.py`)

## Overview

The `owid_config.py` module is the **central configuration hub** for the OWID Commons Categorization project. It manages all paths, directories, credentials, and environment settings used across the application.

## Purpose

This module:
- ✅ Loads environment variables from `.env` file
- ✅ Sets up project directory structure automatically
- ✅ Provides centralized access to paths and credentials
- ✅ Ensures consistent configuration across all scripts
- ✅ Simplifies path management using Python's `pathlib`

---

## Environment Variables

### Required Variables

Create a `.env` file in your project root with the following variables:

```env
# Required for Phase 2 (automated categorization)
WM_USERNAME=your_wikimedia_username
PASSWORD=your_bot_password

# Optional - defaults to current directory if not set
MAIN_DIR=/path/to/your/project/root
```

### Variable Details

#### `MAIN_DIR` (Optional)

**Purpose**: Defines the root directory where all output and log files will be stored.

**Default**: Current directory (`.`) if not specified

**Usage**:
- Controls where `output/` and `logs/` directories are created
- Allows you to organize project data separately from source code
- Useful for running the project from different locations

**Examples**:
```env
# Windows absolute path
MAIN_DIR=C:\Users\YourName\Documents\OWID-data

# Windows relative path
MAIN_DIR=..\..\data

# Linux/Mac absolute path
MAIN_DIR=/home/username/owid-data

# Current directory (default)
MAIN_DIR=.
```

**Recommended Setup**:
```
Project Structure Option 1 (MAIN_DIR=.):
OWID-categories/
├── .env              # MAIN_DIR=.
├── src/
├── output/           # Created here
├── logs/             # Created here
└── README.md

Project Structure Option 2 (MAIN_DIR=../data):
workspace/
├── OWID-categories/
│   ├── .env          # MAIN_DIR=../data
│   ├── src/
│   └── README.md
└── data/
    ├── output/       # Created here
    └── logs/         # Created here
```

#### `WM_USERNAME`

**Purpose**: Your Wikimedia Commons username for authenticated API operations

**Required**: For Phase 2 (running `run_categorize.py`)

**Not Required**: For Phase 1 (running `fetch_commons_files.py` - read-only operations)

**Format**: Your exact Wikimedia Commons username (case-sensitive)

**Example**:
```env
WM_USERNAME=JohnDoe2025
```

#### `PASSWORD`

**Purpose**: Your Wikimedia Commons password or bot password

**Required**: For Phase 2 (automated edits to Commons)

**Security Recommendations**:
- ✅ **Use bot passwords** instead of main account passwords
- ✅ Create bot passwords at: https://commons.wikimedia.org/wiki/Special:BotPasswords
- ✅ Grant only necessary permissions (e.g., "Edit existing pages")
- ✅ Never commit `.env` to version control
- ✅ Add `.env` to `.gitignore`

**Example**:
```env
# Using a bot password (recommended)
PASSWORD=YourBotName@abcdef123456789012345678
```

---

## Directory Structure

When you run any script that imports `owid_config`, the following directories are **automatically created**:

```
{MAIN_DIR}/
├── output/                          # All generated JSON files
│   ├── owid_summary.json    # Summary statistics
│   ├── countries/                   # Per-country files
│   │   ├── CAN.json
│   │   ├── USA.json
│   │   ├── BRA.json
│   │   └── ...
│   └── continents/                  # Per-continent files
│       ├── Africa.json
│       ├── Asia.json
│       ├── Europe.json
│       └── ...
└── logs/                            # Operation logs
    ├── categorize_countries.log     # Country categorization logs
    └── categorize_continents.log    # Continent categorization logs
```

**Note**: Directories are created with `mkdir(exist_ok=True)`, so it's safe to run scripts multiple times.

---

## Exported Configuration Objects

### Path Objects (all are `pathlib.Path` instances)

| Variable | Type | Description | Example Value |
|----------|------|-------------|---------------|
| `MAIN_DIR` | Path | Project root directory | `Path("C:/OWID-data")` |
| `OUTPUT_DIR` | Path | Output directory for JSON files | `Path("C:/OWID-data/output")` |
| `LOG_DIR` | Path | Directory for log files | `Path("C:/OWID-data/logs")` |
| `COUNTRIES_DIR` | Path | Country JSON files directory | `Path("C:/OWID-data/output/countries")` |
| `CONTINENTS_DIR` | Path | Continent JSON files directory | `Path("C:/OWID-data/output/continents")` |
| `LOG_FILE_COUNTRIES` | Path | Country operation log file | `Path("C:/OWID-data/logs/categorize_countries.log")` |
| `LOG_FILE_CONTINENTS` | Path | Continent operation log file | `Path("C:/OWID-data/logs/categorize_continents.log")` |

### Credential Variables (strings or None)

| Variable | Type | Description |
|----------|------|-------------|
| `WM_USERNAME` | str \| None | Wikimedia Commons username |
| `PASSWORD` | str \| None | Wikimedia Commons password/bot password |

---

## Usage Examples

### Basic Import

```python
from owid_config import OUTPUT_DIR, COUNTRIES_DIR, LOG_DIR

# Use paths in your code
print(f"Output directory: {OUTPUT_DIR}")
print(f"Countries directory: {COUNTRIES_DIR}")
```

### Writing Output Files

```python
import json
from owid_config import COUNTRIES_DIR

# Write a country JSON file
country_data = {
    "iso3": "CAN",
    "country": "Canada",
    "graphs": [],
    "maps": []
}

output_file = COUNTRIES_DIR / "CAN.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(country_data, f, indent=2, ensure_ascii=False)

print(f"Saved to: {output_file}")
```

### Setting Up Logging

```python
import logging
from owid_config import LOG_FILE_COUNTRIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_COUNTRIES, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting categorization process")
```

### Checking Credentials

```python
from owid_config import WM_USERNAME, PASSWORD

def check_credentials():
    """Verify that credentials are configured."""
    if not WM_USERNAME or not PASSWORD:
        raise ValueError(
            "Credentials not found. Please set WM_USERNAME and PASSWORD in .env file"
        )
    print(f"✓ Authenticated as: {WM_USERNAME}")

# Use in scripts that require authentication
if __name__ == "__main__":
    check_credentials()
    # ... rest of script
```

### Reading Existing Files

```python
import json
from pathlib import Path
from owid_config import OUTPUT_DIR

# Read the global summary file
summary_file = OUTPUT_DIR / "owid_summary.json"

if summary_file.exists():
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
    print(f"Loaded {len(summary)} countries")
else:
    print("Summary file not found. Run fetch_commons_files.py first.")
```

### Using MAIN_DIR for Custom Paths

```python
from owid_config import MAIN_DIR

# Create custom subdirectories
reports_dir = MAIN_DIR / "reports"
reports_dir.mkdir(exist_ok=True)

# Create custom file paths
custom_report = reports_dir / "analysis_2025.txt"
with open(custom_report, "w") as f:
    f.write("Analysis report")
```

---

## Setup Instructions

### Step 1: Create `.env` File

In your project root, create a file named `.env`:

```bash
# Windows PowerShell
New-Item -Path .env -ItemType File

# Linux/Mac
touch .env
```

### Step 2: Add Configuration

Edit `.env` and add your settings:

```env
# Project directory (optional - defaults to current directory)
MAIN_DIR=.

# Wikimedia Commons credentials (required for Phase 2)
WM_USERNAME=YourUsername
PASSWORD=YourBotPassword@token123456
```

### Step 3: Verify `.gitignore`

Ensure `.env` is in your `.gitignore` file:

```gitignore
# Environment variables (contains credentials)
.env

# Python cache
__pycache__/
*.pyc

# Logs
logs/
*.log

# Output (optional - may want to commit summary files)
output/
```

### Step 4: Test Configuration

Create a test script:

```python
# test_config.py
from owid_config import (
    MAIN_DIR, OUTPUT_DIR, LOG_DIR,
    COUNTRIES_DIR, CONTINENTS_DIR,
    WM_USERNAME, PASSWORD
)

print("Configuration Test")
print("=" * 50)
print(f"MAIN_DIR: {MAIN_DIR}")
print(f"OUTPUT_DIR: {OUTPUT_DIR}")
print(f"LOG_DIR: {LOG_DIR}")
print(f"COUNTRIES_DIR: {COUNTRIES_DIR}")
print(f"CONTINENTS_DIR: {CONTINENTS_DIR}")
print()
print(f"Username configured: {'Yes' if WM_USERNAME else 'No'}")
print(f"Password configured: {'Yes' if PASSWORD else 'No'}")
print()
print("Directory Status:")
print(f"  Output dir exists: {OUTPUT_DIR.exists()}")
print(f"  Log dir exists: {LOG_DIR.exists()}")
print(f"  Countries dir exists: {COUNTRIES_DIR.exists()}")
```

Run the test:
```bash
python test_config.py
```

---

## Integration with Project Scripts

### Phase 1: `fetch_commons_files.py`

```python
from owid_config import OUTPUT_DIR, COUNTRIES_DIR

# Automatically uses configured paths
def save_country_file(iso3: str, data: dict):
    output_file = COUNTRIES_DIR / f"{iso3}.json"
    # ... save logic
```

**No credentials required** - read-only API access

### Phase 2: `run_categorize.py`

```python
from owid_config import WM_USERNAME, PASSWORD, LOG_FILE_COUNTRIES
import mwclient

# Requires credentials
site = mwclient.Site("commons.wikimedia.org")
site.login(WM_USERNAME, PASSWORD)
```

**Credentials required** - writes to Commons

---

## Troubleshooting

### Issue: "Credentials not found"

**Problem**: `WM_USERNAME` or `PASSWORD` is `None`

**Solution**:
1. Verify `.env` file exists in project root
2. Check variable names are exactly `WM_USERNAME` and `PASSWORD`
3. Ensure no extra spaces around `=` in `.env`
4. Restart your Python environment after editing `.env`

### Issue: "Permission denied" when creating directories

**Problem**: Can't create `output/` or `logs/` directories

**Solution**:
1. Check `MAIN_DIR` path has write permissions
2. Verify `MAIN_DIR` exists (parent directory must exist)
3. Run script with appropriate permissions

### Issue: Paths use wrong directory

**Problem**: Files saved to unexpected location

**Solution**:
1. Check `MAIN_DIR` value in `.env`
2. Print `MAIN_DIR` to verify it's being loaded correctly
3. Ensure `.env` is in the correct directory (project root)
4. Use absolute paths in `.env` for clarity

### Issue: `.env` changes not taking effect

**Problem**: Updated `.env` but still using old values

**Solution**:
1. Restart your Python interpreter/IDE
2. Clear `__pycache__` directories
3. Verify you're editing the correct `.env` file
4. Check for multiple `.env` files in parent directories

---

## Security Best Practices

### ✅ DO

- Use bot passwords instead of main account passwords
- Add `.env` to `.gitignore`
- Rotate credentials periodically
- Use separate credentials for development vs. production
- Set minimal permissions on bot passwords
- Store credentials securely (password manager)

### ❌ DON'T

- Commit `.env` to version control
- Share credentials in chat/email
- Use main account password for automation
- Hard-code credentials in scripts
- Grant unnecessary permissions to bots
- Reuse passwords across services

---

## Advanced Configuration

### Using Multiple Environments

Create different `.env` files:

```bash
.env.development
.env.production
.env.testing
```

Load specific environment:

```python
from dotenv import load_dotenv

# Load specific environment
load_dotenv(".env.development")
```

### Overriding Defaults

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Override with fallback chain
MAIN_DIR = Path(
    os.getenv("MAIN_DIR") or
    os.getenv("PROJECT_ROOT") or
    "."
)
```

### Validating Configuration

```python
from owid_config import WM_USERNAME, PASSWORD, MAIN_DIR

def validate_config():
    """Validate configuration before running scripts."""
    errors = []

    if not MAIN_DIR.exists():
        errors.append(f"MAIN_DIR does not exist: {MAIN_DIR}")

    if not WM_USERNAME:
        errors.append("WM_USERNAME not set in .env")

    if not PASSWORD:
        errors.append("PASSWORD not set in .env")

    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(errors))

    print("✓ Configuration valid")

# Run validation
if __name__ == "__main__":
    validate_config()
```

---

## See Also

- **[README.md](README.md)** - Project overview
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[plans/plan.md](plans/plan.md)** - Phase 1 documentation
- **[plans/plan2.md](plans/plan2.md)** - Phase 2 documentation
- **[Python-dotenv Documentation](https://pypi.org/project/python-dotenv/)** - `.env` file handling

---

## Summary

The `owid_config.py` module provides:
- **Centralized configuration** for paths and credentials
- **Automatic directory creation** for outputs and logs
- **Environment-based settings** via `.env` files
- **Secure credential management** separate from code
- **Consistent path handling** using `pathlib.Path`

**Key Takeaway**: All scripts import from `owid_config` to ensure consistent file locations and credential access across the entire project.
