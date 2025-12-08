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
   - Format: `OWID-Commons-Processor/1.0 (contact: your-email@example.com or https://github.com/your-username)`
   - Replace placeholder with actual contact information before making real requests
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

## Testing

### Test Framework
This project uses **pytest** as the primary testing framework. Pytest provides powerful features including:
- Simple test discovery and execution
- Detailed assertion introspection
- Fixtures for test setup/teardown
- Parametrized testing
- Comprehensive plugin ecosystem

### Installation and Setup

#### Installing pytest
```bash
# Basic pytest installation
pip install pytest

# Recommended: Install with coverage and common plugins
pip install pytest pytest-cov pytest-mock

# Or install all dev dependencies (when requirements-dev.txt is available)
pip install -r requirements-dev.txt
```

#### Running Tests

**Basic test execution:**
```bash
# Run all tests
pytest

# Run tests in a specific file
pytest tests/test_fetch_commons.py

# Run tests in a specific directory
pytest tests/

# Run with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_classification"
```

**Using markers to run specific test types:**
```bash
# Run only unit tests
pytest -m unit

# Run only API tests (typically use mocks)
pytest -m api

# Run integration tests
pytest -m integration

# Run quick smoke tests
pytest -m smoke

# Exclude slow tests
pytest -m "not slow"

# Skip tests requiring credentials
pytest -m "not requires_credentials"
```

**Coverage reporting:**
```bash
# Run tests with coverage
pytest --cov=src --cov-report=html

# View coverage in terminal
pytest --cov=src --cov-report=term-missing

# Generate multiple report formats
pytest --cov=src --cov-report=html --cov-report=term --cov-report=xml
```

### Directory Structure and Conventions

```
OWID-categories/
├── src/                             # Main source code
│   ├── categorize/
│   │   ├── wiki.py
│   │   ├── utils.py
│   │   └── __init__.py
│   ├── fetch_commons_files.py       # Phase 1: Fetch and classify files
│   ├── owid_country_codes.py        # Country code mappings
│   ├── run_categorize.py             # Phase 2: Add categories
├── tests/                        # Test directory
│   ├── test_fetch_commons.py    # Tests for fetch module
│   ├── test_categorize.py       # Tests for categorize module
│   ├── example_usage.py         # Usage examples
│   ├── conftest.py              # Pytest fixtures (shared) - create as needed
│   └── fixtures/                # Test data files - create as needed
│       ├── sample_files.json
│       └── mock_responses.json
├── pytest.ini                    # Pytest configuration
└── requirements.txt              # Dependencies
```

### Test Naming and Organization

**File naming:**
- Test files: `test_*.py` or `*_test.py`
- Test files should mirror source structure: `src/module.py` → `tests/test_module.py`

**Test function naming:**
```python
# Good test names - descriptive and clear
def test_classify_graph_file_with_valid_iso3():
def test_classify_map_file_with_country_name():
def test_build_category_name_formats_correctly():
def test_api_request_handles_pagination():
def test_json_output_has_required_fields():

# Use parametrize for similar test cases
@pytest.mark.parametrize("iso3,expected", [
    ("CAN", "Canada"),
    ("USA", "United States"),
    ("BRA", "Brazil"),
])
def test_iso3_to_country_conversion(iso3, expected):
    assert get_country_from_iso3(iso3) == expected
```

**Test class naming (optional):**
```python
class TestFileClassification:
    """Group related tests together."""

    def test_graph_pattern_matching(self):
        pass

    def test_map_pattern_matching(self):
        pass
```

### Test Types and Markers

Use pytest markers to categorize tests (defined in `pytest.ini`):

```python
import pytest

@pytest.mark.unit
def test_parse_filename():
    """Pure unit test with no external dependencies."""
    pass

@pytest.mark.api
def test_fetch_category_members_with_mock(mock_requests):
    """Test API interaction with mocked requests."""
    pass

@pytest.mark.integration
def test_full_processing_pipeline():
    """Test multiple components working together."""
    pass

@pytest.mark.slow
def test_process_large_dataset():
    """Test that takes significant time."""
    pass

@pytest.mark.requires_credentials
def test_actual_commons_connection():
    """Test requiring real .env credentials (skip in CI)."""
    pass

@pytest.mark.smoke
def test_imports_work():
    """Quick sanity check."""
    pass
```

### Mocking and Fixtures for API Testing

**Always mock external API calls** to avoid:
- Network dependencies
- Rate limiting issues
- Inconsistent test results
- Slow test execution

**Using pytest fixtures:**
```python
# tests/conftest.py - Create this file to share fixtures across test modules
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_mediawiki_response():
    """Mock MediaWiki API response."""
    return {
        "query": {
            "categorymembers": [
                {
                    "pageid": 1,
                    "title": "File:Agriculture share gdp, 1997 to 2021, CAN.svg"
                }
            ]
        }
    }

@pytest.fixture
def mock_requests_get(monkeypatch):
    """Mock requests.get for API calls."""
    mock_response = Mock()
    mock_response.json.return_value = {"query": {"categorymembers": []}}
    mock_response.status_code = 200

    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)
    return mock_get

@pytest.fixture
def mock_mwclient_site():
    """Mock mwclient Site object."""
    mock_site = MagicMock()
    mock_page = MagicMock()
    mock_page.exists = True
    mock_page.text.return_value = "Page content\n[[Category:Existing]]"
    mock_site.pages.__getitem__ = Mock(return_value=mock_page)
    return mock_site
```

**Using fixtures in tests:**
```python
def test_fetch_files_from_api(mock_requests_get, mock_mediawiki_response):
    """Test fetching files with mocked API."""
    mock_requests_get.return_value.json.return_value = mock_mediawiki_response

    result = fetch_category_members()

    assert len(result) > 0
    mock_requests_get.assert_called_once()

def test_add_category_to_page(mock_mwclient_site):
    """Test adding category with mocked site."""
    page = mock_mwclient_site.pages["File:Test.svg"]

    # Test categorization logic
    assert page.exists
    assert "Category:Existing" in page.text()
```

**Pytest-mock plugin (recommended):**
```python
def test_with_pytest_mock(mocker):
    """Using pytest-mock plugin."""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"data": "test"}

    # Your test code
    result = fetch_data()
    assert result == {"data": "test"}
```

### Test Data Management

**Use fixtures for test data:**
```python
@pytest.fixture
def sample_file_titles():
    """Sample file titles for testing."""
    return [
        "File:Agriculture share gdp, 1997 to 2021, CAN.svg",
        "File:GDP growth, 2000 to 2023, USA.svg",
        "File:Life expectancy, France, 2019.svg",
    ]

@pytest.fixture
def sample_country_data():
    """Sample country JSON structure."""
    return {
        "iso3": "CAN",
        "country": "Canada",
        "graphs": [],
        "maps": []
    }
```

**Use temporary directories for file operations:**
```python
def test_write_json_files(tmp_path):
    """Test JSON file writing using pytest's tmp_path."""
    output_file = tmp_path / "test_output.json"
    data = {"test": "data"}

    with open(output_file, "w") as f:
        json.dump(data, f)

    assert output_file.exists()
    with open(output_file, "r") as f:
        loaded = json.load(f)
    assert loaded == data
```

### Test Coverage Guidelines

**Target coverage levels:**
- **Overall**: Aim for 80%+ code coverage
- **Critical paths**: 90%+ for core functions (classification, API calls, JSON generation)
- **Error handling**: Cover exception paths and edge cases
- **Documentation**: Don't aim for 100% - focus on meaningful tests

**Coverage exclusions:**
```python
# In your code, mark sections to exclude from coverage
def main():  # pragma: no cover
    """Main entry point - tested manually."""
    pass

if __name__ == "__main__":  # pragma: no cover
    main()
```

**Generate coverage reports:**
```bash
# HTML report (easy to browse)
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing

# Fail if coverage drops below threshold
pytest --cov=src --cov-fail-under=80
```

### CI/CD Testing Considerations

**For GitHub Actions or CI/CD pipelines:**

```yaml
# Example .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: ./coverage.xml
```

**CI-specific test practices:**
- Skip tests requiring credentials: `pytest -m "not requires_credentials"`
- Run quick tests first: `pytest -m smoke` before full suite
- Use coverage reports to track quality trends
- Set coverage thresholds to prevent regressions
- Cache dependencies to speed up CI runs

### Testing Best Practices

**General guidelines:**
1. **Test behavior, not implementation** - Focus on what functions do, not how
2. **One assertion per test** (when possible) - Makes failures clearer
3. **Use descriptive test names** - Test name should explain what's being tested
4. **Keep tests independent** - Tests should not depend on execution order
5. **Mock external dependencies** - Always mock API calls, file I/O can use temp dirs
6. **Test edge cases** - Empty inputs, None values, invalid data
7. **Test error handling** - Verify exceptions are raised appropriately

**For this project specifically:**
```python
# Test file classification patterns
def test_graph_pattern_matches_valid_filename():
    title = "File:Agriculture share gdp, 1997 to 2021, CAN.svg"
    file_type, data = classify_and_parse_file(title)
    assert file_type == "graph"
    assert data["iso3"] == "CAN"
    assert data["start_year"] == 1997
    assert data["end_year"] == 2021

# Test country code mapping
def test_country_code_mapping_handles_missing_code():
    result = get_iso3_from_country("Nonexistent Country")
    assert result is None

# Test API pagination
@pytest.mark.api
def test_fetch_handles_pagination(mock_requests_get):
    # Mock paginated response
    mock_requests_get.side_effect = [
        Mock(json=lambda: {"continue": {"cmcontinue": "token"}, "query": {"categorymembers": [{"pageid": 1}]}}),
        Mock(json=lambda: {"query": {"categorymembers": [{"pageid": 2}]}})
    ]

    results = fetch_all_category_members()
    assert len(results) == 2

# Test JSON structure validation
def test_country_json_has_required_fields(sample_country_data):
    required_fields = ["iso3", "country", "graphs", "maps"]
    for field in required_fields:
        assert field in sample_country_data
```

### Dry-Run Testing Approach

In addition to automated tests:
- **Implement `--dry-run` flags** in scripts for safe testing
- **Log intended actions** instead of executing them
- **Test with small datasets** before full runs (`--limit` parameter)
- **Manually verify** output files after test runs
- **Cross-check statistics** in summary files

### Running Tests During Development

**Recommended workflow:**
```bash
# 1. Run quick smoke tests during development
pytest -m smoke -v

# 2. Run specific test file you're working on
pytest tests/test_fetch_commons.py -v

# 3. Before committing, run all non-credential tests
pytest -m "not requires_credentials" -v

# 4. Periodically check coverage
pytest --cov=src --cov-report=term-missing

# 5. Before PR, run full test suite
pytest -v --cov=src --cov-report=html
```

### Debugging Failed Tests

```bash
# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest --showlocals

# Run last failed tests only
pytest --lf

# Run failed tests first, then others
pytest --ff

# Verbose output with full diffs
pytest -vv
```

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
