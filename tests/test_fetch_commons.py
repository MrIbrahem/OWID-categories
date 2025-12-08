#!/usr/bin/env python3
"""
Test script for OWID Commons processing with sample data.

This script demonstrates the functionality without requiring network access.
"""

import json
import sys
from pathlib import Path
import pytest

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetch_commons_files import (
    classify_and_parse_file,
    fetch_files,
    write_country_json_files,
    write_summary_json,
    OUTPUT_DIR,
    COUNTRIES_DIR
)


def create_sample_data() -> list[str]:
    """Create sample file data for testing."""
    return [
        "File:Agriculture share gdp, 1997 to 2021, CAN.svg",
        "File:Access to clean fuels and technologies for cooking, Canada, 1990.svg",
        "File:Agriculture share gdp, 2000 to 2022, USA.svg",
        "File:CO2 emissions, 1990 to 2021, GBR.svg",
        "File:Educational attainment, Germany, 2018.svg",
        "File:GDP per capita, United States, 2020.svg",
        "File:Income inequality, 1980 to 2020, DEU.svg",
        "File:Life expectancy, 1950 to 2020, BRA.svg",
        "File:Population density, Brazil, 2019.svg",
        "File:Renewable energy share, United Kingdom, 2021.svg",
    ]


@pytest.mark.unit
def test_classification():
    """Test file classification logic."""
    # Test graph file with ISO3 code
    file_type, parsed_data = classify_and_parse_file(
        "File:Agriculture share gdp, 1997 to 2021, CAN.svg"
    )
    assert file_type == "graph", "Should classify as graph"
    assert parsed_data is not None, "Should parse data successfully"
    assert parsed_data['iso3'] == "CAN", "Should extract correct ISO3 code"
    assert parsed_data['start_year'] == 1997, "Should extract correct start year"
    assert parsed_data['end_year'] == 2021, "Should extract correct end year"
    assert 'indicator' in parsed_data, "Should have indicator field"

    # Test map file with country name
    file_type, parsed_data = classify_and_parse_file(
        "File:Access to clean fuels and technologies for cooking, Canada, 1990.svg"
    )
    assert file_type == "map", "Should classify as map"
    assert parsed_data is not None, "Should parse data successfully"
    assert parsed_data['region'] == "Canada", "Should extract correct region"
    assert parsed_data['year'] == 1990, "Should extract correct year"
    assert 'indicator' in parsed_data, "Should have indicator field"

    # Test map file with country name (United States)
    file_type, parsed_data = classify_and_parse_file(
        "File:GDP per capita, United States, 2020.svg"
    )
    assert file_type == "map", "Should classify as map"
    assert parsed_data['region'] == "United States", "Should extract correct region"
    assert parsed_data['year'] == 2020, "Should extract correct year"

    # Test unknown file type
    file_type, parsed_data = classify_and_parse_file(
        "File:Some other file.png"
    )
    assert file_type is None, "Should return None for unknown file type"
    assert parsed_data is None, "Should return None for unknown file data"


@pytest.mark.integration
def test_processing():
    """Test full processing pipeline with sample data."""
    # Create sample data
    sample_files = create_sample_data()
    assert len(sample_files) == 10, "Should have 10 sample files"

    # Process files
    countries, continents, not_matched = fetch_files(sample_files)

    # Assertions on processed data
    assert len(countries) > 0, "Should process at least one country"
    assert "CAN" in countries, "Should have Canada (CAN)"
    assert "USA" in countries, "Should have United States (USA)"
    assert "BRA" in countries, "Should have Brazil (BRA)"
    assert "GBR" in countries, "Should have United Kingdom (GBR)"
    assert "DEU" in countries, "Should have Germany (DEU)"

    # Check structure of country data
    for iso3, data in countries.items():
        assert 'country' in data, f"Country data for {iso3} should have 'country' field"
        assert 'iso3' in data, f"Country data for {iso3} should have 'iso3' field"
        assert 'graphs' in data, f"Country data for {iso3} should have 'graphs' field"
        assert 'maps' in data, f"Country data for {iso3} should have 'maps' field"
        assert isinstance(data['graphs'], list), f"Graphs for {iso3} should be a list"
        assert isinstance(data['maps'], list), f"Maps for {iso3} should be a list"
        assert data['iso3'] == iso3, "ISO3 code should match key"

    # Check specific country data
    can_data = countries["CAN"]
    assert can_data['country'] == "Canada", "Canada should have correct country name"
    assert len(can_data['graphs']) > 0, "Canada should have at least one graph"
    assert len(can_data['maps']) > 0, "Canada should have at least one map"

    # Write output files
    write_country_json_files(countries)
    write_summary_json(countries, continents)

    # Verify output files were created
    assert COUNTRIES_DIR.exists(), "Countries directory should be created"
    assert (OUTPUT_DIR / 'owid_summary.json').exists(), "Summary file should be created"

    # Verify summary content
    summary_file = OUTPUT_DIR / "owid_summary.json"
    with open(summary_file, "r") as f:
        summary = json.load(f)

    assert isinstance(summary, dict), "Summary should be a dict"
    assert len(summary["countries"]) == len(countries), "Summary should have entry for each country"

    for entry in summary["countries"]:
        assert 'iso3' in entry, "Summary entry should have iso3"
        assert 'country' in entry, "Summary entry should have country"
        assert 'graph_count' in entry, "Summary entry should have graph_count"
        assert 'map_count' in entry, "Summary entry should have map_count"
        assert isinstance(entry['graph_count'], int), "graph_count should be integer"
        assert isinstance(entry['map_count'], int), "map_count should be integer"
