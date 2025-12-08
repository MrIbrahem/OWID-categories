#!/usr/bin/env python3
"""
OWID Commons File Fetcher and Processor

This script fetches all files from Category:Uploaded_by_OWID_importer_tool on Wikimedia Commons,
classifies them as graphs or maps, extracts country codes, and generates JSON output files.

Requirements:
- Python 3.10+ (uses union type syntax: str | None)
- requests library
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple
from owid_country_codes import get_country_from_iso3, get_iso3_from_country
from owid_config import OUTPUT_DIR, LOG_DIR, COUNTRIES_DIR

from categorize import (
    get_category_members_petscan,
    # fetch_category_members,
)
from utils import normalize_title, setup_logging

logger = logging.getLogger(__name__)

# Configuration
CATEGORY_NAME = "Category:Uploaded_by_OWID_importer_tool"
SUMMARY_FILE = OUTPUT_DIR / "owid_summary.json"
LOG_FILE = LOG_DIR / "fetch_commons.log"

# List of continents for classification
CONTINENTS = {
    "Africa", "Antarctica", "Asia", "Europe", "North America",
    "South America", "Oceania", "Americas", "World"
}

# Regex patterns for classification
GRAPH_PATTERN = re.compile(r",\s*(\d+)\s+to\s+(\d+),\s*(\w+)\.svg$")
# Map pattern: country/region name followed by a single year
# The region/country name should start with a letter and can contain letters, spaces, hyphens, and parentheses
# Note: Hyphen is at the end of character class to avoid being interpreted as a range
MAP_PATTERN = re.compile(r",\s*([A-Z][A-Za-z \(\)-]+),\s*(\d+)\.svg$")


def classify_and_parse_file(title: str) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Classify a file as graph, map, continent_map, or unknown and extract relevant information.

    Args:
        title: Full file title

    Returns:
        Tuple of (file_type, parsed_data) where:
        - file_type is "graph", "map", "continent_map", or None
        - parsed_data is a dict with extracted fields
    """
    # Try graph pattern first
    graph_match = GRAPH_PATTERN.search(title)
    if graph_match:
        start_year, end_year, iso3 = graph_match.groups()

        # Extract indicator (everything before the first comma in the normalized name)
        base_name = normalize_title(title)
        first_comma = base_name.find(",")
        indicator = base_name[:first_comma].strip() if first_comma != -1 else base_name

        return "graph", {
            "iso3": iso3,
            "indicator": indicator,
            "start_year": int(start_year),
            "end_year": int(end_year)
        }

    # Try map pattern
    map_match = MAP_PATTERN.search(title)
    if map_match:
        region, year = map_match.groups()
        region = region.strip()

        # Extract indicator
        base_name = normalize_title(title)
        first_comma = base_name.find(",")
        indicator = base_name[:first_comma].strip() if first_comma != -1 else base_name

        # Check if region is a continent
        if region in CONTINENTS:
            return "continent_map", {
                "continent": region,
                "indicator": indicator,
                "year": int(year)
            }

        # Try to resolve region to ISO3
        iso3 = get_iso3_from_country(region)

        return "map", {
            "iso3": iso3,
            "region": region,
            "indicator": indicator,
            "year": int(year)
        }
    # Unknown file type
    return None, None


def build_file_page_url(title: str) -> str:
    """
    Build the Commons page URL for a file.

    Args:
        title: Full file title

    Returns:
        Commons page URL
    """
    return "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")


def fetch_files(files: List[str]) -> Tuple[Dict[str, Dict], Dict[str, Dict], List[str]]:
    """
    Process all files and aggregate them by country and continent.

    Args:
        files: List of file dictionaries from API

    Returns:
        Tuple of (countries, continents, not_matched) where:
        - countries: Dictionary keyed by ISO3 code with country data
        - continents: Dictionary keyed by continent name with continent data
        - not_matched: List of unmatched file titles
    """
    countries = {}
    continents = {}
    stats = {
        "graph_count": 0,
        "map_count": 0,
        "continent_map_count": 0,
        "unknown_count": 0,
        "unresolved_region_count": 0
    }

    logger.info("Starting file classification and aggregation")

    not_matched = []
    for title in files:

        file_type, parsed_data = classify_and_parse_file(title)

        if not file_type or not parsed_data:
            stats["unknown_count"] += 1
            logger.debug(f"Unknown file type: {title}")
            not_matched.append(title)
            continue

        # Handle continent maps separately
        if file_type == "continent_map":
            continent = parsed_data["continent"]

            # Initialize continent entry if needed
            if continent not in continents:
                continents[continent] = {
                    "continent": continent,
                    "graphs": [],
                    "maps": [],
                    "unknowns": []
                }

            # Build entry
            file_page = build_file_page_url(title)
            entry = {
                "title": title,
                "indicator": parsed_data["indicator"],
                "year": parsed_data["year"],
                "file_page": file_page
            }
            continents[continent]["maps"].append(entry)
            stats["continent_map_count"] += 1
            continue

        iso3 = parsed_data.get("iso3")

        if not iso3:
            stats["unresolved_region_count"] += 1
            logger.debug(f"Could not resolve region: {title}")
            not_matched.append(title)
            continue

        # Initialize country entry if needed
        if iso3 not in countries:
            country_name = get_country_from_iso3(iso3)
            if not country_name:
                logger.warning(f"Unknown ISO3 code: {iso3}")

            countries[iso3] = {
                "iso3": iso3,
                "country": country_name,
                "graphs": [],
                "maps": [],
                "unknowns": []
            }

        # Build entry
        file_page = build_file_page_url(title)

        if file_type == "graph":
            entry = {
                "title": title,
                "indicator": parsed_data["indicator"],
                "start_year": parsed_data["start_year"],
                "end_year": parsed_data["end_year"],
                "file_page": file_page
            }
            countries[iso3]["graphs"].append(entry)
            stats["graph_count"] += 1

        elif file_type == "map":
            entry = {
                "title": title,
                "indicator": parsed_data["indicator"],
                "year": parsed_data["year"],
                "region": parsed_data["region"],
                "file_page": file_page
            }
            countries[iso3]["maps"].append(entry)
            stats["map_count"] += 1

    logger.info("Classification complete:")
    logger.info(f"  Graphs: {stats['graph_count']}")
    logger.info(f"  Maps: {stats['map_count']}")
    logger.info(f"  Continent maps: {stats['continent_map_count']}")
    logger.info(f"  Unknown: {stats['unknown_count']}")
    logger.info(f"  Unresolved regions: {stats['unresolved_region_count']}")
    logger.info(f"  Countries with data: {len(countries)}")
    logger.info(f"  Continents with data: {len(continents)}")

    return countries, continents, not_matched


def write_country_json_files(countries: Dict[str, Dict]):
    """
    Write individual JSON files for each country.

    Args:
        countries: Dictionary of country data keyed by ISO3
    """
    COUNTRIES_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Writing {len(countries)} country JSON files")

    for iso3, data in countries.items():
        file_path = COUNTRIES_DIR / f"{iso3}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Country JSON files written to {COUNTRIES_DIR}")


def write_continent_json_files(continents: Dict[str, Dict]):
    """
    Write individual JSON files for each continent.

    Args:
        continents: Dictionary of continent data keyed by continent name
    """
    CONTINENTS_DIR = OUTPUT_DIR / "continents"
    CONTINENTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Writing {len(continents)} continent JSON files")

    for continent, data in continents.items():
        # Use continent name as filename (replace spaces with underscores)
        safe_name = continent.replace(" ", "_")
        file_path = CONTINENTS_DIR / f"{safe_name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Continent JSON files written to {CONTINENTS_DIR}")


def write_summary_json(countries: Dict[str, Dict], continents: Dict[str, Dict]) -> None:
    """
    Write global summary JSON file including countries and continents.

    Args:
        countries: Dictionary of country data keyed by ISO3
        continents: Dictionary of continent data keyed by continent name
    """
    summary = {
        "countries": [],
        "continents": []
    }

    for iso3, data in sorted(countries.items()):
        summary["countries"].append({
            "iso3": iso3,
            "country": data["country"],
            "graph_count": len(data["graphs"]),
            "map_count": len(data["maps"])
        })

    for continent, data in sorted(continents.items()):
        summary["continents"].append({
            "continent": continent,
            "map_count": len(data["maps"])
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(f"Summary JSON written to {SUMMARY_FILE}")


def write_not_matched_files(not_matched: List[str]) -> None:
    """
    Write a text file listing files that could not be matched.

    Args:
        not_matched: List of file titles that were not matched
    """
    if not not_matched:
        logger.info("No unmatched files to write.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    not_matched_file = OUTPUT_DIR / "not_matched_files.txt"

    with open(not_matched_file, "w", encoding="utf-8") as f:
        for title in not_matched:
            f.write(f"{title}\n")

    logger.info(f"Unmatched files written to {not_matched_file}")


def main() -> None:
    """Main execution function."""
    setup_logging(LOG_FILE)

    # Fetch all files from the category
    # files = fetch_category_members(CATEGORY_NAME)
    files = get_category_members_petscan(CATEGORY_NAME)

    # Process and aggregate files by country and continent
    countries, continents, not_matched = fetch_files(files)

    # Write output files
    write_country_json_files(countries)
    write_continent_json_files(continents)
    write_summary_json(countries, continents)
    write_not_matched_files(not_matched)

    logger.info("Processing complete!")


if __name__ == "__main__":
    main()
