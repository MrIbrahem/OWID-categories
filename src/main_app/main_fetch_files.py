#!/usr/bin/env python3
"""
OWID Commons File Fetcher and Processor

This script fetches all files from Category:Uploaded_by_OWID_importer_tool on Wikimedia Commons,
classifies them as graphs or maps, extracts country codes, and generates JSON output files.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .api_services import (
    MwClientPage,
    get_category_count,
    get_category_members_titles,
)
from .categorize import connect_to_commons
from .categorize.wikitext_report import create_wikitext_report, make_report_data
from .files_classifier import classify_and_parse_file
from .files_dumper import (
    load_category_members_from_json,
    save_category_members,
    save_wikitext_report,
    write_continent_json_files,
    write_country_json_files,
    write_not_matched_files,
    write_summary_json,
)
from .owid_config import CATEGORY_NAME, REPORT_PAGE, load_credentials
from .owid_country_codes import get_country_from_iso3, ISO3_TO_COUNTRY_NOT_READY

logger = logging.getLogger(__name__)


@dataclass
class FilesClassess:
    """Aggregated file classification results."""

    countries: Dict[str, Dict]
    continents: Dict[str, Dict]
    not_matched: List[str]
    not_matched_data: Dict[str, List[str]]


def build_file_page_url(title: str) -> str:
    """
    Build the Commons page URL for a file.

    Args:
        title: Full file title

    Returns:
        Commons page URL
    """
    return "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")


def fetch_files(files: List[str]) -> FilesClassess:
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
        "unresolved_region_count": 0,
    }

    logger.info("Starting file classification and aggregation")

    not_matched_data = {
        "unknown": [],
        "unresolved_region": [],
    }

    not_matched = []

    for title in files:

        file_type, parsed_data = classify_and_parse_file(title)

        if not file_type or not parsed_data:
            stats["unknown_count"] += 1
            logger.debug(f"Unknown file type: {title}")
            not_matched.append(title)
            not_matched_data["unknown"].append(title)
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
                    "unknowns": [],
                }

            # Build entry
            file_page = build_file_page_url(title)
            entry = {
                "title": title,
                "indicator": parsed_data["indicator"],
                "file_page": file_page,
            }
            continents[continent]["maps"].append(entry)
            stats["continent_map_count"] += 1
            continue

        iso3 = parsed_data.get("iso3")

        if not iso3:
            stats["unresolved_region_count"] += 1
            logger.debug(f"Could not resolve region: {title}")
            not_matched.append(title)
            not_matched_data["unresolved_region"].append(title)
            continue

        if iso3 in ISO3_TO_COUNTRY_NOT_READY:
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
                "unknowns": [],
            }

        # Build entry
        file_page = build_file_page_url(title)

        if file_type == "graph":
            entry = {
                "title": title,
                "indicator": parsed_data["indicator"],
                "file_page": file_page,
            }
            countries[iso3]["graphs"].append(entry)
            stats["graph_count"] += 1

        elif file_type == "map":
            entry = {
                "title": title,
                "indicator": parsed_data["indicator"],
                "region": parsed_data["region"],
                "file_page": file_page,
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

    return FilesClassess(
        countries=countries,
        continents=continents,
        not_matched=not_matched,
        not_matched_data=not_matched_data,
    )


def load_files(load_from_json: bool) -> Tuple[List[str], int]:
    """Load category member titles from cache or Wikimedia Commons."""
    files = []
    total_pages = 0

    # Fetch all files from the category
    if load_from_json:
        files = load_category_members_from_json()
        total_pages = len(files)

    if files:
        return files, total_pages

    total_pages = get_category_count(CATEGORY_NAME) or 0

    # Load credentials
    username, password = load_credentials()
    if not username or not password:
        logger.error("Failed to load credentials from .env file")
        logger.error("Please create a .env file with WIKIPEDIA_BOT_USERNAME and WIKIPEDIA_BOT_PASSWORD")
        return [], total_pages

    # Connect to Commons
    site = connect_to_commons(username, password)
    if not site:
        logger.error("Failed to connect to Wikimedia Commons")
        return [], total_pages

    files = get_category_members_titles(
        site,
        CATEGORY_NAME,
        namespace=6,
    )

    if len(files) == total_pages:
        save_category_members(files)
        logger.info(f"Successfully fetched {len(files)} files from the category")

    return files, total_pages


def get_site() -> None | Any:
    username, password = load_credentials()
    if not username or not password:
        logger.error("Failed to load credentials from .env file")
        logger.error("Please create a .env file with WIKIPEDIA_BOT_USERNAME and WIKIPEDIA_BOT_PASSWORD")
        return None

    # Connect to Commons
    site = connect_to_commons(username, password)
    if not site:
        logger.error("Failed to connect to Wikimedia Commons")
        return None
    return site


def fetch_files_entry(
    load_from_json: bool = False,
) -> None:
    """Main execution function."""

    files, total_pages = load_files(load_from_json)

    # Process and aggregate files by country and continent
    fetch_data = fetch_files(files)

    files_summary = {
        "total": total_pages,
        "matched": total_pages - len(fetch_data.not_matched),
        "not_matched": {x: len(v) for x, v in fetch_data.not_matched_data.items()},
    }
    # Write output files
    write_summary_json(
        fetch_data.countries,
        fetch_data.continents,
        files_summary=files_summary,
    )

    write_country_json_files(fetch_data.countries)
    write_continent_json_files(fetch_data.continents)
    write_not_matched_files(fetch_data.not_matched_data)

    site = get_site()

    report_data = make_report_data(
        site,
        fetch_data.countries,
        fetch_data.continents,
    )

    wikitext = create_wikitext_report(report_data)
    save_wikitext_report(report_data, wikitext)

    if site:
        logger.info(f"Saving wikitext report to {REPORT_PAGE}")
        page = MwClientPage(REPORT_PAGE, site)
        page.edit(wikitext, "Update OWID report", nocreate=False)

    logger.info("Processing complete!")


__all__ = [
    "fetch_files_entry",
]
