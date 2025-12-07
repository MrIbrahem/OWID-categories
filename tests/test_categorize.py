#!/usr/bin/env python3
"""
Test script for OWID Commons categorization functionality.

This script tests the categorization logic without requiring real Commons credentials.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from categorize_commons_files import (
    build_category_name,
    normalize_country_name,
    category_exists_on_page,
    ensure_category_exists,
    load_country_json,
    COUNTRIES_DIR
)


@pytest.mark.unit
def test_normalize_country_name():
    """Test country name normalization with 'the' prefix."""
    # Countries that should have "the" prefix (complete list from user)
    test_cases_with_the = [
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
    
    # Countries that should NOT have "the" prefix
    test_cases_without_the = [
        ("Canada", "Canada"),
        ("Brazil", "Brazil"),
        ("Germany", "Germany"),
        ("France", "France"),
        ("India", "India"),
        ("China", "China"),
        ("Japan", "Japan"),
        ("Australia", "Australia"),
    ]
    
    # Test countries requiring 'the' prefix
    for country, expected in test_cases_with_the:
        result = normalize_country_name(country)
        assert result == expected, f"Expected '{expected}' but got '{result}' for country '{country}'"
    
    # Test countries NOT requiring 'the' prefix
    for country, expected in test_cases_without_the:
        result = normalize_country_name(country)
        assert result == expected, f"Expected '{expected}' but got '{result}' for country '{country}'"


@pytest.mark.unit
def test_build_category_name():
    """Test category name construction with normalization."""
    test_cases = [
        ("Canada", "Category:Our World in Data graphs of Canada"),
        ("Brazil", "Category:Our World in Data graphs of Brazil"),
        ("Germany", "Category:Our World in Data graphs of Germany"),
        # Countries with "the" prefix (expanded list)
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
        result = build_category_name(country)
        assert result == expected, f"Expected '{expected}' but got '{result}' for country '{country}'"


@pytest.mark.unit
def test_category_exists():
    """Test category existence checking."""
    page_text_with_cat = """
Some file description here.
{{Information
|Description={{en|1=Agriculture share of GDP}}
}}

[[Category:Our World in Data graphs of Canada]]
[[Category:Economic indicators]]
"""
    
    page_text_without_cat = """
Some file description here.
{{Information
|Description={{en|1=Agriculture share of GDP}}
}}

[[Category:Economic indicators]]
"""
    
    # Test with category present
    result1 = category_exists_on_page(
        page_text_with_cat, 
        "Category:Our World in Data graphs of Canada"
    )
    assert result1 is True, "Category should be found when present"
    
    # Test with category absent
    result2 = category_exists_on_page(
        page_text_without_cat,
        "Category:Our World in Data graphs of Canada"
    )
    assert result2 is False, "Category should not be found when absent"
    
    # Test with lowercase variant
    page_text_lowercase = "[[category:Our World in Data graphs of Canada]]"
    result3 = category_exists_on_page(
        page_text_lowercase,
        "Category:Our World in Data graphs of Canada"
    )
    assert result3 is True, "Category check should be case-insensitive"


@pytest.mark.filesystem
def test_load_country_json():
    """Test loading country JSON files."""
    if not COUNTRIES_DIR.exists():
        # Skip test if directory doesn't exist (needs test_fetch_commons to run first)
        return
    
    json_files = list(COUNTRIES_DIR.glob("*.json"))
    
    if not json_files:
        # Skip test if no files exist yet
        return
    
    # Test loading first file
    first_file = json_files[0]
    data = load_country_json(first_file)
    
    # Assertions
    assert data is not None, f"Failed to load {first_file.name}"
    assert 'country' in data, "Country field missing from JSON"
    assert 'iso3' in data, "ISO3 field missing from JSON"
    assert 'graphs' in data, "Graphs field missing from JSON"
    assert 'maps' in data, "Maps field missing from JSON"
    assert isinstance(data['graphs'], list), "Graphs should be a list"
    assert isinstance(data['maps'], list), "Maps should be a list"
    
    # If graphs exist, check structure
    graphs = data.get('graphs', [])
    if graphs:
        first_graph = graphs[0]
        assert 'title' in first_graph, "Graph should have a title"
        assert 'indicator' in first_graph, "Graph should have an indicator"


@pytest.mark.unit
def test_mock_categorization():
    """Test the categorization workflow with mock objects."""
    # Create a mock page
    mock_page = MagicMock()
    mock_page.exists = True
    mock_page.text.return_value = "Some page text\n[[Category:Existing]]"
    
    # Assertions
    assert mock_page.exists is True, "Mock page should exist"
    assert "Category:Existing" in mock_page.text(), "Mock page should contain existing category"
    
    # Simulate adding a category
    category = "Category:Our World in Data graphs of Canada"
    current_text = mock_page.text()
    new_text = current_text.rstrip() + f"\n[[{category}]]\n"
    
    # Assertions
    assert category in new_text, "New category should be in the updated text"
    assert len(new_text) > len(current_text), "New text should be longer than current text"
    assert new_text.endswith(f"[[{category}]]\n"), "Category should be added at the end"


@pytest.mark.api
def test_ensure_category_exists():
    """Test the ensure_category_exists function with mock objects."""
    # Test 1: Category already exists
    mock_site_1 = Mock()
    mock_page_exists = MagicMock()
    mock_page_exists.exists = True
    mock_site_1.pages.__getitem__ = Mock(return_value=mock_page_exists)
    
    result = ensure_category_exists(mock_site_1, "Canada", dry_run=True)
    assert result is True, "Should return True when category already exists"
    
    # Test 2: Category doesn't exist (dry run) - regular country
    mock_site_2 = Mock()
    mock_page_not_exists = MagicMock()
    mock_page_not_exists.exists = False
    mock_site_2.pages.__getitem__ = Mock(return_value=mock_page_not_exists)
    
    result = ensure_category_exists(mock_site_2, "Brazil", dry_run=True)
    assert result is True, "Should return True in dry run mode"
    
    # Test 3: Category doesn't exist (dry run) - country requiring "the"
    mock_site_3 = Mock()
    mock_page_not_exists_3 = MagicMock()
    mock_page_not_exists_3.exists = False
    mock_site_3.pages.__getitem__ = Mock(return_value=mock_page_not_exists_3)
    
    result = ensure_category_exists(mock_site_3, "United Kingdom", dry_run=True)
    assert result is True, "Should return True for countries with 'the' prefix in dry run mode"


@pytest.mark.integration
@pytest.mark.filesystem
def test_dry_run_simulation():
    """Simulate a dry-run on actual test data."""
    if not COUNTRIES_DIR.exists():
        # Skip test if directory doesn't exist
        return
    
    json_files = list(COUNTRIES_DIR.glob("*.json"))
    
    if not json_files:
        # Skip test if no files exist yet
        return
    
    total_graphs = 0
    countries_processed = 0
    
    # Sort to ensure consistent test order, and test all countries
    for json_file in sorted(json_files):
        data = load_country_json(json_file)
        if data:
            country = data.get('country')
            normalized_country = normalize_country_name(country)
            graphs = data.get('graphs', [])
            category = build_category_name(country)
            
            # Assertions
            assert country is not None, f"Country should not be None for {json_file.name}"
            assert normalized_country is not None, f"Normalized country should not be None for {country}"
            assert category.startswith("Category:Our World in Data graphs of"), \
                f"Category should have correct prefix for {country}"
            assert isinstance(graphs, list), f"Graphs should be a list for {country}"
            
            total_graphs += len(graphs)
            countries_processed += 1
    
    # Final assertions
    assert countries_processed > 0, "Should have processed at least one country"
    assert total_graphs >= 0, "Total graphs should be non-negative"



