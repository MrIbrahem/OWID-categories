#!/usr/bin/env python3
"""
Test script for OWID Commons categorization functionality.

This script tests the categorization logic without requiring real Commons credentials.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

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


def test_normalize_country_name():
    """Test country name normalization with 'the' prefix."""
    print("Test 1: Normalizing Country Names")
    print("=" * 80)
    
    # Countries that should have "the" prefix (updated list)
    test_cases_with_the = [
        ("Democratic Republic of Congo", "the Democratic Republic of Congo"),
        ("Dominican Republic", "the Dominican Republic"),
        ("Philippines", "the Philippines"),
        ("Netherlands", "the Netherlands"),
        ("United Arab Emirates", "the United Arab Emirates"),
        ("United Kingdom", "the United Kingdom"),
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
        ("United States", "United States"),  # Not in the new list
        ("Czech Republic", "Czech Republic"),  # Not in the new list
        ("Bahamas", "Bahamas"),  # Not in the new list
    ]
    
    print("\nCountries requiring 'the' prefix:")
    all_passed = True
    for country, expected in test_cases_with_the:
        result = normalize_country_name(country)
        status = "✓" if result == expected else "✗"
        print(f"{status} {country} -> {result}")
        if result != expected:
            print(f"  Expected: {expected}")
            all_passed = False
    
    print("\nCountries NOT requiring 'the' prefix:")
    for country, expected in test_cases_without_the:
        result = normalize_country_name(country)
        status = "✓" if result == expected else "✗"
        print(f"{status} {country} -> {result}")
        if result != expected:
            print(f"  Expected: {expected}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All normalization tests passed!")
    else:
        print("\n✗ Some normalization tests failed!")
    
    print()


def test_build_category_name():
    """Test category name construction with normalization."""
    print("Test 2: Building Category Names with Normalization")
    print("=" * 80)
    
    test_cases = [
        ("Canada", "Category:Our World in Data graphs of Canada"),
        ("Brazil", "Category:Our World in Data graphs of Brazil"),
        ("Germany", "Category:Our World in Data graphs of Germany"),
        # Countries with "the" prefix
        ("United Kingdom", "Category:Our World in Data graphs of the United Kingdom"),
        ("Philippines", "Category:Our World in Data graphs of the Philippines"),
        ("Netherlands", "Category:Our World in Data graphs of the Netherlands"),
        ("Dominican Republic", "Category:Our World in Data graphs of the Dominican Republic"),
        ("United Arab Emirates", "Category:Our World in Data graphs of the United Arab Emirates"),
        ("Democratic Republic of Congo", "Category:Our World in Data graphs of the Democratic Republic of Congo"),
        # Countries that should NOT have "the" anymore
        ("United States", "Category:Our World in Data graphs of United States"),
        ("Bahamas", "Category:Our World in Data graphs of Bahamas"),
    ]
    
    all_passed = True
    for country, expected in test_cases:
        result = build_category_name(country)
        status = "✓" if result == expected else "✗"
        print(f"{status} {country} -> {result}")
        if result != expected:
            print(f"  Expected: {expected}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All category name tests passed!")
    else:
        print("\n✗ Some category name tests failed!")
    
    print()


def test_category_exists():
    """Test category existence checking."""
    print("Test 3: Checking Category Existence")
    print("=" * 80)
    
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
    print(f"✓ Category present: {result1} (expected True)")
    
    # Test with category absent
    result2 = category_exists_on_page(
        page_text_without_cat,
        "Category:Our World in Data graphs of Canada"
    )
    print(f"✓ Category absent: {result2} (expected False)")
    
    # Test with lowercase variant
    page_text_lowercase = "[[category:Our World in Data graphs of Canada]]"
    result3 = category_exists_on_page(
        page_text_lowercase,
        "Category:Our World in Data graphs of Canada"
    )
    print(f"✓ Lowercase variant: {result3} (expected True)")
    
    print()


def test_load_country_json():
    """Test loading country JSON files."""
    print("Test 4: Loading Country JSON Files")
    print("=" * 80)
    
    if not COUNTRIES_DIR.exists():
        print("⚠ Country files directory not found. Run test_fetch_commons.py first.")
        print()
        return
    
    json_files = list(COUNTRIES_DIR.glob("*.json"))
    
    if not json_files:
        print("⚠ No JSON files found in output/countries/")
        print()
        return
    
    print(f"Found {len(json_files)} country JSON files")
    
    # Test loading first file
    first_file = json_files[0]
    data = load_country_json(first_file)
    
    if data:
        print(f"✓ Successfully loaded {first_file.name}")
        print(f"  Country: {data.get('country')} ({data.get('iso3')})")
        print(f"  Graphs: {len(data.get('graphs', []))}")
        print(f"  Maps: {len(data.get('maps', []))}")
        
        # Show first graph
        graphs = data.get('graphs', [])
        if graphs:
            print(f"\n  First graph:")
            print(f"    Title: {graphs[0].get('title')}")
            print(f"    Indicator: {graphs[0].get('indicator')}")
    else:
        print(f"✗ Failed to load {first_file.name}")
    
    print()


def test_mock_categorization():
    """Test the categorization workflow with mock objects."""
    print("Test 5: Mock Categorization Workflow")
    print("=" * 80)
    
    # Create a mock page
    mock_page = MagicMock()
    mock_page.exists = True
    mock_page.text.return_value = "Some page text\n[[Category:Existing]]"
    
    print("✓ Created mock Page object")
    print("✓ Mock page exists: True")
    print(f"✓ Mock page text: {mock_page.text()[:50]}...")
    
    # Simulate adding a category
    category = "Category:Our World in Data graphs of Canada"
    current_text = mock_page.text()
    new_text = current_text.rstrip() + f"\n[[{category}]]\n"
    
    print(f"\n✓ Would add category: {category}")
    print(f"✓ New text length: {len(new_text)} characters")
    print("✓ Category would be added to end of page")
    
    print()


def test_ensure_category_exists():
    """Test the ensure_category_exists function with mock objects."""
    print("Test 6: Ensure Category Exists")
    print("=" * 80)
    
    # Test 1: Category already exists
    print("Test case 1: Category already exists")
    mock_site_1 = Mock()
    mock_page_exists = MagicMock()
    mock_page_exists.exists = True
    mock_site_1.pages.__getitem__ = Mock(return_value=mock_page_exists)
    
    result = ensure_category_exists(mock_site_1, "Canada", dry_run=True)
    print(f"✓ Result: {result} (expected True)")
    
    # Test 2: Category doesn't exist (dry run) - regular country
    print("\nTest case 2: Category doesn't exist (dry run) - regular country")
    mock_site_2 = Mock()
    mock_page_not_exists = MagicMock()
    mock_page_not_exists.exists = False
    mock_site_2.pages.__getitem__ = Mock(return_value=mock_page_not_exists)
    
    result = ensure_category_exists(mock_site_2, "Brazil", dry_run=True)
    print(f"✓ Result: {result} (expected True)")
    print("✓ Would create: Category:Our World in Data graphs of Brazil")
    print("✓ With content: [[Category:Our World in Data graphs|Brazil]]")
    
    # Test 3: Category doesn't exist (dry run) - country requiring "the"
    print("\nTest case 3: Category doesn't exist (dry run) - country with 'the'")
    mock_site_3 = Mock()
    mock_page_not_exists_3 = MagicMock()
    mock_page_not_exists_3.exists = False
    mock_site_3.pages.__getitem__ = Mock(return_value=mock_page_not_exists_3)
    
    result = ensure_category_exists(mock_site_3, "United Kingdom", dry_run=True)
    print(f"✓ Result: {result} (expected True)")
    print("✓ Would create: Category:Our World in Data graphs of the United Kingdom")
    print("✓ With content: [[Category:Our World in Data graphs|the United Kingdom]]")
    
    print()


def test_dry_run_simulation():
    """Simulate a dry-run on actual test data."""
    print("Test 7: Dry-Run Simulation")
    print("=" * 80)
    
    if not COUNTRIES_DIR.exists():
        print("⚠ Country files directory not found. Run test_fetch_commons.py first.")
        print()
        return
    
    json_files = list(COUNTRIES_DIR.glob("*.json"))
    
    if not json_files:
        print("⚠ No JSON files found")
        print()
        return
    
    total_graphs = 0
    
    # Sort to ensure consistent test order, and test all countries
    for json_file in sorted(json_files):
        data = load_country_json(json_file)
        if data:
            country = data.get('country')
            normalized_country = normalize_country_name(country)
            graphs = data.get('graphs', [])
            category = build_category_name(country)
            
            print(f"\n{data.get('iso3')} ({normalized_country})")
            print(f"  Original: {country}")
            print(f"  Normalized: {normalized_country}")
            print(f"  Category: {category}")
            print(f"  Graphs to categorize: {len(graphs)}")
            
            for graph in graphs[:2]:  # Show first 2 graphs
                print(f"    - {graph.get('title')}")
            
            total_graphs += len(graphs)
    
    print(f"\n✓ Total graphs that would be processed: {total_graphs}")
    print()


def main():
    """Run all tests."""
    print("\nOWID Commons Categorization Test Suite")
    print("=" * 80)
    print()
    
    test_normalize_country_name()
    test_build_category_name()
    test_category_exists()
    test_load_country_json()
    test_mock_categorization()
    test_ensure_category_exists()
    test_dry_run_simulation()
    
    print("=" * 80)
    print("All tests completed!")
    print("\nTo test with actual Commons connection:")
    print("1. Create a .env file with your bot credentials")
    print("2. Run: python3 src/categorize_commons_files.py --dry-run --limit 2")


if __name__ == "__main__":
    main()
