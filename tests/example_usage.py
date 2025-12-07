#!/usr/bin/env python3
"""
Example usage of the OWID Commons processing tools.

This script demonstrates how to use the various functions in the package.
"""

import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetch_commons_files import (
    classify_and_parse_file,
    build_file_page_url,
    OUTPUT_DIR,
    COUNTRIES_DIR
)
from owid_country_codes import get_iso3_from_country, get_country_from_iso3


def example_classify_files():
    """Example of classifying individual files."""
    print("Example 1: Classifying Files")
    print("=" * 80)
    
    examples = [
        "File:Agriculture share gdp, 1997 to 2021, CAN.svg",
        "File:GDP growth, 2000 to 2023, USA.svg",
        "File:Life expectancy, France, 2019.svg",
        "File:CO2 emissions, China, 2020.svg"
    ]
    
    for title in examples:
        file_type, data = classify_and_parse_file(title)
        print(f"\nFile: {title}")
        print(f"  Type: {file_type}")
        if data:
            print(f"  ISO3: {data.get('iso3')}")
            print(f"  Indicator: {data.get('indicator')}")
            if file_type == "graph":
                print(f"  Years: {data.get('start_year')} to {data.get('end_year')}")
            elif file_type == "map":
                print(f"  Year: {data.get('year')}")
                print(f"  Region: {data.get('region')}")
    
    print("\n" + "=" * 80 + "\n")


def example_country_lookups():
    """Example of country code lookups."""
    print("Example 2: Country Code Lookups")
    print("=" * 80)
    
    # ISO3 to country name
    iso3_codes = ["CAN", "USA", "BRA", "GBR", "DEU", "FRA", "JPN"]
    print("\nISO3 to Country Name:")
    for iso3 in iso3_codes:
        country = get_country_from_iso3(iso3)
        print(f"  {iso3} -> {country}")
    
    # Country name to ISO3
    countries = ["Canada", "United States", "Brazil", "United Kingdom", "Germany"]
    print("\nCountry Name to ISO3:")
    for country in countries:
        iso3 = get_iso3_from_country(country)
        print(f"  {country} -> {iso3}")
    
    print("\n" + "=" * 80 + "\n")


def example_read_output_files():
    """Example of reading generated output files."""
    print("Example 3: Reading Output Files")
    print("=" * 80)
    
    # Check if output files exist
    summary_file = OUTPUT_DIR / "owid_country_summary.json"
    
    if not summary_file.exists():
        print("\nNo output files found. Run fetch_commons_files.py or test_fetch_commons.py first.")
        print("=" * 80 + "\n")
        return
    
    # Read summary
    with open(summary_file, "r") as f:
        summary = json.load(f)
    
    print(f"\nGlobal Summary ({len(summary)} countries):")
    for entry in summary[:5]:  # Show first 5
        print(f"  {entry['iso3']} ({entry['country']}): "
              f"{entry['graph_count']} graphs, {entry['map_count']} maps")
    
    if len(summary) > 5:
        print(f"  ... and {len(summary) - 5} more countries")
    
    # Read a specific country file
    if COUNTRIES_DIR.exists():
        country_files = list(COUNTRIES_DIR.glob("*.json"))
        if country_files:
            example_file = country_files[0]
            print(f"\nExample Country File: {example_file.name}")
            with open(example_file, "r") as f:
                data = json.load(f)
            
            print(f"  Country: {data['country']} ({data['iso3']})")
            print(f"  Graphs: {len(data['graphs'])}")
            print(f"  Maps: {len(data['maps'])}")
            
            if data['graphs']:
                print(f"\n  First graph:")
                graph = data['graphs'][0]
                print(f"    Indicator: {graph['indicator']}")
                print(f"    Years: {graph['start_year']} to {graph['end_year']}")
            
            if data['maps']:
                print(f"\n  First map:")
                map_entry = data['maps'][0]
                print(f"    Indicator: {map_entry['indicator']}")
                print(f"    Year: {map_entry['year']}")
    
    print("\n" + "=" * 80 + "\n")


def example_build_urls():
    """Example of building Commons URLs."""
    print("Example 4: Building Commons URLs")
    print("=" * 80)
    
    titles = [
        "File:Agriculture share gdp, 1997 to 2021, CAN.svg",
        "File:Life expectancy, United States, 2020.svg"
    ]
    
    print("\nCommons Page URLs:")
    for title in titles:
        url = build_file_page_url(title)
        print(f"  {title}")
        print(f"    -> {url}")
    
    print("\n" + "=" * 80 + "\n")



