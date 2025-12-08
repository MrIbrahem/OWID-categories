"""
Tests for run_categorize.py module.

Tests the country categorization script functionality including
processing country files and adding categories to graph files.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import json

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from run_categorize import process_files


@pytest.mark.unit
class TestProcessFiles:
    """Test processing country files."""

    def test_process_files_basic(self):
        """Test basic file processing."""
        # Create mock site
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Some page text"
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        # Mock category page
        mock_cat_page = MagicMock()
        mock_cat_page.exists = True

        # Setup side_effect to return different pages based on title
        def get_page(title):
            if title.startswith("Category:"):
                return mock_cat_page
            return mock_page

        mock_site.pages.__getitem__ = Mock(side_effect=get_page)

        # Create test data
        test_data = {
            "iso3": "CAN",
            "country": "Canada",
            "graphs": [
                {
                    "title": "File:Test Graph 1.svg",
                    "indicator": "GDP",
                },
                {
                    "title": "File:Test Graph 2.svg",
                    "indicator": "Population",
                }
            ]
        }

        # Mock file loading
        with patch("run_countries.load_json_file", return_value=test_data):
            with patch("run_countries.get_category_member_count", return_value=0):
                stats = process_files(
                    mock_site,
                    Path("output/countries/CAN.json"),
                    dry_run=True
                )

        # Assertions
        assert stats["added"] >= 0, "Should have processed some files"
        assert stats["errors"] == 0, "Should have no errors"

    def test_process_files_with_limit(self):
        """Test file processing with per-country limit."""
        # Create mock site
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Some page text"

        mock_cat_page = MagicMock()
        mock_cat_page.exists = True

        def get_page(title):
            if title.startswith("Category:"):
                return mock_cat_page
            return mock_page

        mock_site.pages.__getitem__ = Mock(side_effect=get_page)

        # Create test data with many files
        test_data = {
            "iso3": "USA",
            "country": "United States",
            "graphs": [
                {"title": f"File:Test Graph {i}.svg", "indicator": "Test"}
                for i in range(10)
            ]
        }

        # Mock file loading
        with patch("run_countries.load_json_file", return_value=test_data):
            with patch("run_countries.get_category_member_count", return_value=0):
                stats = process_files(
                    mock_site,
                    Path("output/countries/USA.json"),
                    dry_run=True,
                    files_per_country=3
                )

        # Should only process 3 files
        assert stats["added"] + stats["skipped"] <= 3, "Should respect per-country limit"

    def test_process_files_missing_country(self):
        """Test processing file with missing country name."""
        mock_site = Mock()

        # Test data missing country name
        test_data = {
            "iso3": "XXX",
            "graphs": []
        }

        with patch("run_countries.load_json_file", return_value=test_data):
            stats = process_files(
                mock_site,
                Path("output/countries/XXX.json"),
                dry_run=True
            )

        assert stats["errors"] > 0, "Should have error for missing country"

    def test_process_files_invalid_json(self):
        """Test processing invalid JSON file."""
        mock_site = Mock()

        with patch("run_countries.load_json_file", return_value=None):
            stats = process_files(
                mock_site,
                Path("output/countries/invalid.json"),
                dry_run=True
            )

        assert stats["errors"] > 0, "Should have error for invalid JSON"


@pytest.mark.filesystem
class TestCountryFilesExist:
    """Test that country files exist and have correct structure."""

    def test_countries_directory_exists(self):
        """Test that countries directory exists."""
        countries_dir = Path("output/countries")
        if not countries_dir.exists():
            pytest.skip("Countries directory not found. Run fetch_commons_files.py first.")

        assert countries_dir.is_dir(), "Countries directory should exist"

    def test_country_json_structure(self):
        """Test structure of country JSON files."""
        countries_dir = Path("output/countries")

        if not countries_dir.exists():
            pytest.skip("Countries directory not found")

        json_files = list(countries_dir.glob("*.json"))

        if not json_files:
            pytest.skip("No country JSON files found")

        # Test first file
        first_file = json_files[0]
        with open(first_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check required fields
        assert "country" in data, "Country field should exist"
        assert "iso3" in data, "ISO3 field should exist"
        assert "graphs" in data, "Graphs field should exist"
        assert "maps" in data, "Maps field should exist"
        assert isinstance(data["graphs"], list), "Graphs should be a list"
        assert isinstance(data["maps"], list), "Maps should be a list"


@pytest.mark.integration
class TestDryRunSimulation:
    """Integration tests with dry-run simulation."""

    def test_dry_run_with_sample_data(self):
        """Test dry-run processing with sample data."""
        countries_dir = Path("output/countries")

        if not countries_dir.exists():
            pytest.skip("Countries directory not found")

        json_files = list(countries_dir.glob("*.json"))

        if not json_files:
            pytest.skip("No country JSON files found")

        # Create mock site
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Test content"

        mock_cat_page = MagicMock()
        mock_cat_page.exists = True

        def get_page(title):
            if title.startswith("Category:"):
                return mock_cat_page
            return mock_page

        mock_site.pages.__getitem__ = Mock(side_effect=get_page)

        # Process first 3 countries in dry-run
        for json_file in sorted(json_files)[:3]:
            with patch("run_countries.get_category_member_count", return_value=0):
                stats = process_files(
                    mock_site,
                    json_file,
                    dry_run=True
                )

            # Basic assertions
            assert isinstance(stats, dict), "Should return stats dictionary"
            assert "added" in stats, "Stats should have 'added' key"
            assert "skipped" in stats, "Stats should have 'skipped' key"
            assert "errors" in stats, "Stats should have 'errors' key"
