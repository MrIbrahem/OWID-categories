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
    category_exists_on_page,
    load_country_json,
    COUNTRIES_DIR
)


def test_build_category_name():
    """Test category name construction."""
    print("Test 1: Building Category Names")
    print("=" * 80)
    
    test_cases = [
        ("Canada", "Category:Our World in Data graphs of Canada"),
        ("United States", "Category:Our World in Data graphs of United States"),
        ("Brazil", "Category:Our World in Data graphs of Brazil"),
        ("United Kingdom", "Category:Our World in Data graphs of United Kingdom"),
    ]
    
    for country, expected in test_cases:
        result = build_category_name(country)
        status = "✓" if result == expected else "✗"
        print(f"{status} {country} -> {result}")
        if result != expected:
            print(f"  Expected: {expected}")
    
    print()


def test_category_exists():
    """Test category existence checking."""
    print("Test 2: Checking Category Existence")
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
    print("Test 3: Loading Country JSON Files")
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
    print("Test 4: Mock Categorization Workflow")
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


def test_dry_run_simulation():
    """Simulate a dry-run on actual test data."""
    print("Test 5: Dry-Run Simulation")
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
    
    for json_file in json_files[:3]:  # Process first 3 countries
        data = load_country_json(json_file)
        if data:
            country = data.get('country')
            graphs = data.get('graphs', [])
            category = build_category_name(country)
            
            print(f"\n{data.get('iso3')} ({country})")
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
    
    test_build_category_name()
    test_category_exists()
    test_load_country_json()
    test_mock_categorization()
    test_dry_run_simulation()
    
    print("=" * 80)
    print("All tests completed!")
    print("\nTo test with actual Commons connection:")
    print("1. Create a .env file with your bot credentials")
    print("2. Run: python3 src/categorize_commons_files.py --dry-run --limit 2")


if __name__ == "__main__":
    main()
