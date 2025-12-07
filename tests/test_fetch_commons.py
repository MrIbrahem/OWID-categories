#!/usr/bin/env python3
"""
Test script for OWID Commons processing with sample data.

This script demonstrates the functionality without requiring network access.
"""

import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetch_commons_files import (
    classify_and_parse_file,
    build_file_page_url,
    process_files,
    write_country_json_files,
    write_summary_json,
    OUTPUT_DIR,
    COUNTRIES_DIR
)


def create_sample_data():
    """Create sample file data for testing."""
    return [
        {
            "pageid": 1,
            "title": "File:Agriculture share gdp, 1997 to 2021, CAN.svg"
        },
        {
            "pageid": 2,
            "title": "File:Agriculture share gdp, 2000 to 2022, USA.svg"
        },
        {
            "pageid": 3,
            "title": "File:Access to clean fuels and technologies for cooking, Canada, 1990.svg"
        },
        {
            "pageid": 4,
            "title": "File:GDP per capita, United States, 2020.svg"
        },
        {
            "pageid": 5,
            "title": "File:Life expectancy, 1950 to 2020, BRA.svg"
        },
        {
            "pageid": 6,
            "title": "File:Population density, Brazil, 2019.svg"
        },
        {
            "pageid": 7,
            "title": "File:CO2 emissions, 1990 to 2021, GBR.svg"
        },
        {
            "pageid": 8,
            "title": "File:Renewable energy share, United Kingdom, 2021.svg"
        },
        {
            "pageid": 9,
            "title": "File:Income inequality, 1980 to 2020, DEU.svg"
        },
        {
            "pageid": 10,
            "title": "File:Educational attainment, Germany, 2018.svg"
        }
    ]


def test_classification():
    """Test file classification logic."""
    print("Testing file classification...")
    print("=" * 80)
    
    test_cases = [
        "File:Agriculture share gdp, 1997 to 2021, CAN.svg",
        "File:Access to clean fuels and technologies for cooking, Canada, 1990.svg",
        "File:GDP per capita, United States, 2020.svg",
        "File:Some other file.png"
    ]
    
    for title in test_cases:
        file_type, parsed_data = classify_and_parse_file(title)
        print(f"\nTitle: {title}")
        print(f"  Type: {file_type}")
        print(f"  Data: {parsed_data}")
    
    print("\n" + "=" * 80)


def test_processing():
    """Test full processing pipeline with sample data."""
    print("\nTesting full processing pipeline...")
    print("=" * 80)
    
    # Create sample data
    sample_files = create_sample_data()
    print(f"\nProcessing {len(sample_files)} sample files")
    
    # Process files
    countries = process_files(sample_files)
    
    print(f"\nCountries found: {len(countries)}")
    for iso3, data in sorted(countries.items()):
        print(f"\n{iso3} ({data['country']}):")
        print(f"  Graphs: {len(data['graphs'])}")
        print(f"  Maps: {len(data['maps'])}")
    
    # Write output files
    write_country_json_files(countries)
    write_summary_json(countries)
    
    print("\n" + "=" * 80)
    print("\nOutput files created:")
    print(f"  Countries directory: {COUNTRIES_DIR}")
    print(f"  Summary file: {OUTPUT_DIR / 'owid_country_summary.json'}")
    
    # Display summary content
    summary_file = OUTPUT_DIR / "owid_country_summary.json"
    if summary_file.exists():
        with open(summary_file, "r") as f:
            summary = json.load(f)
        print("\nSummary content:")
        for entry in summary:
            print(f"  {entry['iso3']} ({entry['country']}): "
                  f"{entry['graph_count']} graphs, {entry['map_count']} maps")
    
    print("\n" + "=" * 80)



