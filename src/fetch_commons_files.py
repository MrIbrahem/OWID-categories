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
import urllib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from owid_country_codes import get_country_from_iso3, get_iso3_from_country

logger = logging.getLogger(__name__)

# Configuration
API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"
CATEGORY_NAME = "Category:Uploaded_by_OWID_importer_tool"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
COUNTRIES_DIR = OUTPUT_DIR / "countries"
SUMMARY_FILE = OUTPUT_DIR / "owid_country_summary.json"
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "fetch_commons.log"

# User-Agent header (required by Wikimedia)
USER_AGENT = "OWID-Commons-Processor/1.0 (https://github.com/MrIbrahem/OWID-categories; contact via GitHub)"

# Regex patterns for classification
GRAPH_PATTERN = re.compile(r",\s*(\d+)\s+to\s+(\d+),\s*(\w+)\.svg$")
# Map pattern: country/region name followed by a single year
# The region/country name should start with a letter and can contain letters, spaces, hyphens, and parentheses
# Note: Hyphen is at the end of character class to avoid being interpreted as a range
MAP_PATTERN = re.compile(r",\s*([A-Z][A-Za-z \(\)-]+),\s*(\d+)\.svg$")


def setup_logging():
    """Set up logging configuration."""
    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_category_members_petscan(category) -> list | list[str]:
    """
    Fetch all pages belonging to a given category from a Wikimedia project using the Petscan API.
    """
    # Build PetScan URL for the given category
    base_url = "https://petscan.wmflabs.org/"

    if category.lower().startswith("category:"):
        category = category[9:]

    params = {
        "language": "commons",
        "project": "wikimedia",
        "categories": f"{category}",
        "format": "plain",
        "depth": 0,
        "ns[6]": 1,
        "doit": "Do it!"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    logger.info(f"petscan url: {url}")

    headers = {}
    headers["User-Agent"] = USER_AGENT
    text = ""
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        text = resp.text
    except Exception as e:
        logger.error(f"get_petscan_category_pages: request/json error: {e}")
        return []

    if not text:
        logger.warning("get_petscan_category_pages: empty response")
        return []

    result = [x.strip() for x in text.splitlines()]
    logger.debug(f"get_petscan_category_pages: found {len(result)} members")
    return result


def fetch_category_members() -> List[Dict]:
    """
    Fetch all files from the OWID category using MediaWiki API with pagination.

    Returns:
        List of file dictionaries with 'pageid', 'title', etc.
    """
    all_files = []
    cmcontinue = None
    page_count = 0

    logger.info(f"Starting to fetch files from {CATEGORY_NAME}")

    while True:
        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": CATEGORY_NAME,
            "cmtype": "file",
            "cmlimit": "max"
        }

        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        try:
            response = requests.get(
                API_ENDPOINT,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            members = data.get("query", {}).get("categorymembers", [])
            all_files.extend([x.get("title", "") for x in members])
            page_count += 1

            logger.info(f"Fetched page {page_count}: {len(members)} files (total: {len(all_files)})")

            if "continue" in data:
                cmcontinue = data["continue"].get("cmcontinue")
            else:
                break

        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    logger.info(f"Finished fetching {len(all_files)} files in {page_count} pages")
    return all_files


def normalize_title(title: str) -> str:
    """
    Remove 'File:' prefix and return base name.

    Args:
        title: Full file title like "File:Something.svg"

    Returns:
        Base name without prefix
    """
    if title.startswith("File:"):
        return title[5:]
    return title


def classify_and_parse_file(title: str) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Classify a file as graph, map, or unknown and extract relevant information.

    Args:
        title: Full file title

    Returns:
        Tuple of (file_type, parsed_data) where:
        - file_type is "graph", "map", or None
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


def process_files(files: List[str]) -> Dict[str, Dict]:
    """
    Process all files and aggregate them by country.

    Args:
        files: List of file dictionaries from API

    Returns:
        Dictionary keyed by ISO3 code with country data
    """
    countries = {}
    stats = {
        "graph_count": 0,
        "map_count": 0,
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
    logger.info(f"  Unknown: {stats['unknown_count']}")
    logger.info(f"  Unresolved regions: {stats['unresolved_region_count']}")
    logger.info(f"  Countries with data: {len(countries)}")

    return countries, not_matched


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


def write_summary_json(countries: Dict[str, Dict]):
    """
    Write global summary JSON file.

    Args:
        countries: Dictionary of country data keyed by ISO3
    """
    summary = []

    for iso3, data in sorted(countries.items()):
        summary.append({
            "iso3": iso3,
            "country": data["country"],
            "graph_count": len(data["graphs"]),
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
    setup_logging()

    # Fetch all files from the category
    # files = fetch_category_members()
    files = get_category_members_petscan(CATEGORY_NAME)

    # Process and aggregate files by country
    countries, not_matched = process_files(files)

    # Write output files
    write_country_json_files(countries)
    write_summary_json(countries)
    write_not_matched_files(not_matched)

    logger.info("Processing complete!")


if __name__ == "__main__":
    main()
