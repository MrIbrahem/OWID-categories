"""
Tests for main_app.main_run_categorize.py module.

Tests the country categorization script functionality including
processing country files and adding categories to graph files.
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.main_app.main_run_categorize import process_files
from src.main_app.owid_config import COUNTRIES_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_site():
    """Create a mock mwclient site with page and category page lookups."""
    mock = Mock()
    mock_page = MagicMock()
    mock_page.exists = True
    mock_page.text.return_value = "Some page text"

    mock_cat_page = MagicMock()
    mock_cat_page.exists = True

    def get_page(title):
        return mock_cat_page if title.startswith("Category:") else mock_page

    mock.pages.__getitem__ = Mock(side_effect=get_page)
    return mock


@pytest.fixture
def mock_api_calls():
    """Patch network-dependent calls used by process_files."""
    with (
        patch("src.main_app.main_run_categorize.get_category_count", return_value=0),
        patch("src.main_app.main_run_categorize.get_category_members_titles", return_value=[]),
        patch("src.main_app.main_run_categorize.resolve_category_redirect", side_effect=lambda s, c: c),
    ):
        yield


# ---------------------------------------------------------------------------
# Unit tests – isolated processing logic
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProcessFiles:
    """Test processing country files."""

    def test_process_files_basic(self, mock_site, mock_api_calls):
        """Test basic file processing."""
        data = {
            "iso3": "CAN",
            "country": "Canada",
            "graphs": [
                {"title": "File:Test Graph 1.svg", "indicator": "GDP"},
                {"title": "File:Test Graph 2.svg", "indicator": "Population"},
            ],
        }
        with patch("src.main_app.main_run_categorize.load_json_file", return_value=data):
            stats = process_files(mock_site, COUNTRIES_DIR / "CAN.json", dry_run=True)

        assert stats["added"] >= 0
        assert stats["errors"] == 0

    def test_process_files_with_limit(self, mock_site, mock_api_calls):
        """Test file processing with per-country limit."""
        data = {
            "iso3": "USA",
            "country": "United States",
            "graphs": [{"title": f"File:Test Graph {i}.svg", "indicator": "Test"} for i in range(10)],
        }
        with patch("src.main_app.main_run_categorize.load_json_file", return_value=data):
            stats = process_files(mock_site, COUNTRIES_DIR / "USA.json", dry_run=True, files_per_one=3)

        assert stats["added"] + stats["skipped"] <= 3

    def test_process_files_missing_country(self, mock_site):
        """Test processing file with missing country name."""
        with patch("src.main_app.main_run_categorize.load_json_file", return_value={"iso3": "XXX", "graphs": []}):
            stats = process_files(mock_site, COUNTRIES_DIR / "XXX.json", dry_run=True)

        assert stats["errors"] > 0

    def test_process_files_invalid_json(self, mock_site):
        """Test processing invalid JSON file (None returned by loader)."""
        with patch("src.main_app.main_run_categorize.load_json_file", return_value=None):
            stats = process_files(mock_site, COUNTRIES_DIR / "invalid.json", dry_run=True)

        assert stats["errors"] > 0


# ---------------------------------------------------------------------------
# Filesystem tests – real data structure validation
# ---------------------------------------------------------------------------


@pytest.mark.filesystem
class TestCountryFilesExist:
    """Test that country files exist and have correct structure."""

    def test_countries_directory_exists(self):
        """Test that countries directory exists."""
        if not COUNTRIES_DIR.exists():
            pytest.skip("Countries directory not found. Run fetch_commons_files.py first.")

        assert COUNTRIES_DIR.is_dir()

    def test_country_json_structure(self):
        """Test structure of country JSON files."""
        if not COUNTRIES_DIR.exists():
            pytest.skip("Countries directory not found")

        json_files = sorted(COUNTRIES_DIR.glob("*.json"))
        if not json_files:
            pytest.skip("No country JSON files found")

        with open(json_files[0], encoding="utf-8") as f:
            data = json.load(f)

        assert "country" in data
        assert "iso3" in data
        assert "graphs" in data
        assert "maps" in data
        assert isinstance(data["graphs"], list)
        assert isinstance(data["maps"], list)


# ---------------------------------------------------------------------------
# Integration tests – dry-run with real data files
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestDryRunSimulation:
    """Integration tests with dry-run simulation."""

    def test_dry_run_with_sample_data(self, mock_site, mock_api_calls):
        """Test dry-run processing with sample data."""
        if not COUNTRIES_DIR.exists():
            pytest.skip("Countries directory not found")

        json_files = sorted(COUNTRIES_DIR.glob("*.json"))
        if not json_files:
            pytest.skip("No country JSON files found")

        for json_file in json_files[:3]:
            with patch("src.main_app.main_run_categorize.load_json_file") as m:
                m.return_value = {
                    "iso3": json_file.stem,
                    "country": json_file.stem,
                    "graphs": [],
                }
                stats = process_files(mock_site, json_file, dry_run=True)

            assert isinstance(stats, dict)
            assert "added" in stats
            assert "skipped" in stats
            assert "errors" in stats
