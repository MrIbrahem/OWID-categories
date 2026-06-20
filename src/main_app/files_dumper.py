#!/usr/bin/env python3
""" """

import json
import logging
from typing import Dict, List

from .owid_config import (
    CONTINENTS_DIR,
    COUNTRIES_DIR,
    OUTPUT_DIR,
    SUMMARY_FILE,
)

logger = logging.getLogger(__name__)

# List of continents for classification
CONTINENTS = {
    "Africa",
    "Antarctica",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "Oceania",
    "Americas",
    "World",
}


def write_country_json_files(countries: Dict[str, Dict]):
    """
    Write individual JSON files for each country.

    Args:
        countries: Dictionary of country data keyed by ISO3
    """

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

    logger.info(f"Writing {len(continents)} continent JSON files")

    for continent, data in continents.items():
        # Use continent name as filename (replace spaces with underscores)
        safe_name = continent.replace(" ", "_")
        file_path = CONTINENTS_DIR / f"{safe_name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Continent JSON files written to {CONTINENTS_DIR}")


def write_summary_json(
    countries: Dict[str, Dict],
    continents: Dict[str, Dict],
) -> None:
    """
    Write global summary JSON file including countries and continents.

    Args:
        countries: Dictionary of country data keyed by ISO3
        continents: Dictionary of continent data keyed by continent name
    """
    summary = {"countries": [], "continents": []}

    for iso3, data in sorted(countries.items()):
        summary["countries"].append(
            {
                "iso3": iso3,
                "country": data["country"],
                "graph_count": len(data["graphs"]),
                "map_count": len(data["maps"]),
            }
        )

    for continent, data in sorted(continents.items()):
        summary["continents"].append({"continent": continent, "map_count": len(data["maps"])})

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

    not_matched_file = OUTPUT_DIR / "not_matched_files.txt"

    with open(not_matched_file, "w", encoding="utf-8") as f:
        for title in not_matched:
            f.write(f"{title}\n")

    logger.info(f"Unmatched files written to {not_matched_file}")


def save_category_members(data: list[str]) -> None:
    """ """
    file_path = OUTPUT_DIR / "category_members.json"

    logger.info(f"Writing {len(data)} files into category_members.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write category members to {file_path}: {e}")


__all__ = [
    "write_country_json_files",
    "write_continent_json_files",
    "write_summary_json",
    "write_not_matched_files",
    "save_category_members",
]
