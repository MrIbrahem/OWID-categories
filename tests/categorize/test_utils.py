"""
Tests for categorize.utils module.

Tests utility functions for country name normalization, category building,
and JSON file loading.
"""

import sys
from pathlib import Path
import pytest
import json
from unittest.mock import Mock, patch, mock_open

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from categorize.utils import (
    normalize_country_name,
    build_category_name,
    get_parent_category,
    load_json_file,
)


@pytest.mark.unit
class TestNormalizeCountryName:
    """Test country name normalization with 'the' prefix."""

    def test_countries_with_the_prefix(self):
        """Test countries that should have 'the' prefix."""
        test_cases = [
            ("Democratic Republic of Congo", "the Democratic Republic of Congo"),
            ("Dominican Republic", "the Dominican Republic"),
            ("Philippines", "the Philippines"),
            ("Netherlands", "the Netherlands"),
            ("United Arab Emirates", "the United Arab Emirates"),
            ("United Kingdom", "the United Kingdom"),
            ("United States", "the United States"),
            ("Czech Republic", "the Czech Republic"),
            ("Central African Republic", "the Central African Republic"),
            ("Maldives", "the Maldives"),
            ("Seychelles", "the Seychelles"),
            ("Bahamas", "the Bahamas"),
            ("Marshall Islands", "the Marshall Islands"),
            ("Solomon Islands", "the Solomon Islands"),
            ("Comoros", "the Comoros"),
            ("Gambia", "the Gambia"),
            ("Vatican City", "the Vatican City"),
            ("Vatican", "the Vatican"),
        ]

        for country, expected in test_cases:
            result = normalize_country_name(country)
            assert result == expected, f"Expected '{expected}' but got '{result}' for country '{country}'"

    def test_countries_without_the_prefix(self):
        """Test countries that should NOT have 'the' prefix."""
        test_cases = [
            ("Canada", "Canada"),
            ("Brazil", "Brazil"),
            ("Germany", "Germany"),
            ("France", "France"),
            ("India", "India"),
            ("China", "China"),
            ("Japan", "Japan"),
            ("Australia", "Australia"),
            ("Mexico", "Mexico"),
            ("Egypt", "Egypt"),
        ]

        for country, expected in test_cases:
            result = normalize_country_name(country)
            assert result == expected, f"Expected '{expected}' but got '{result}' for country '{country}'"


@pytest.mark.unit
class TestBuildCategoryName:
    """Test category name construction."""

    def test_regular_countries(self):
        """Test category names for regular countries."""
        test_cases = [
            ("Canada", "Category:Our World in Data graphs of Canada"),
            ("Brazil", "Category:Our World in Data graphs of Brazil"),
            ("Germany", "Category:Our World in Data graphs of Germany"),
            ("France", "Category:Our World in Data graphs of France"),
        ]

        for country, expected in test_cases:
            result = build_category_name(country, "country", "graphs")
            assert result == expected, f"Expected '{expected}' but got '{result}' for country '{country}'"

    def test_countries_with_the_prefix(self):
        """Test category names for countries requiring 'the' prefix."""
        test_cases = [
            ("United Kingdom", "Category:Our World in Data graphs of the United Kingdom"),
            ("United States", "Category:Our World in Data graphs of the United States"),
            ("Philippines", "Category:Our World in Data graphs of the Philippines"),
            ("Netherlands", "Category:Our World in Data graphs of the Netherlands"),
            ("Dominican Republic", "Category:Our World in Data graphs of the Dominican Republic"),
            ("United Arab Emirates", "Category:Our World in Data graphs of the United Arab Emirates"),
            ("Czech Republic", "Category:Our World in Data graphs of the Czech Republic"),
            ("Central African Republic", "Category:Our World in Data graphs of the Central African Republic"),
            ("Bahamas", "Category:Our World in Data graphs of the Bahamas"),
            ("Maldives", "Category:Our World in Data graphs of the Maldives"),
            ("Seychelles", "Category:Our World in Data graphs of the Seychelles"),
        ]

        for country, expected in test_cases:
            result = build_category_name(country, "country", "graphs")
            assert result == expected, f"Expected '{expected}' but got '{result}' for country '{country}'"

    def test_continents(self):
        """Test category names for continents."""
        test_cases = [
            ("Africa", "Category:Our World in Data graphs of Africa"),
            ("Asia", "Category:Our World in Data graphs of Asia"),
            ("Europe", "Category:Our World in Data graphs of Europe"),
            ("North America", "Category:Our World in Data graphs of North America"),
            ("South America", "Category:Our World in Data graphs of South America"),
            ("Oceania", "Category:Our World in Data graphs of Oceania"),
        ]

        for continent, expected in test_cases:
            result = build_category_name(continent, "continent", "graphs")
            assert result == expected, f"Expected '{expected}' but got '{result}' for continent '{continent}'"

    def test_predefined_categories(self):
        """Test predefined categories like World."""
        result = build_category_name("World", "country", "graphs")
        assert result == "Category:Our World in Data graphs of the world"

        result_maps = build_category_name("World", "country", "maps")
        assert result_maps == "Category:Our World in Data maps of the world"

    def test_maps_type(self):
        """Test category names for maps."""
        result = build_category_name("Canada", "country", "maps")
        assert result == "Category:Our World in Data maps of Canada"


@pytest.mark.unit
class TestGetParentCategory:
    """Test parent category retrieval."""

    def test_country_parent_category(self):
        """Test parent category for countries."""
        result = get_parent_category("country")
        assert result == "Our World in Data graphs by country"

    def test_continent_parent_category(self):
        """Test parent category for continents."""
        result = get_parent_category("continent")
        assert result == "Our World in Data graphs by continent"


@pytest.mark.unit
class TestLoadJsonFile:
    """Test JSON file loading."""

    def test_load_valid_json(self):
        """Test loading a valid JSON file."""
        test_data = {
            "iso3": "CAN",
            "country": "Canada",
            "graphs": [],
            "maps": []
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            result = load_json_file(Path("test.json"))

        assert result is not None
        assert result["iso3"] == "CAN"
        assert result["country"] == "Canada"
        assert "graphs" in result
        assert "maps" in result

    def test_load_invalid_json(self):
        """Test loading an invalid JSON file."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            result = load_json_file(Path("invalid.json"))

        assert result is None

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent file."""
        result = load_json_file(Path("nonexistent.json"))
        assert result is None
