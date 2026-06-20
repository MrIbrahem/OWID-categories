#!/usr/bin/env python3
""" """

import json
import logging
from pathlib import Path
from typing import Dict, List

from .owid_config import (
    CONTINENTS_DIR,
    COUNTRIES_DIR,
    OUTPUT_DIR,
    SUMMARY_FILE,
    SUMMARY_FILE_BACKUP,
)

logger = logging.getLogger(__name__)


def dump_to_file(
    data,
    file: Path,
) -> None:
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write data JSON to {file}: {e}")


def write_country_json_files(countries: Dict[str, Dict]):
    """
    Write individual JSON files for each country.

    Args:
        countries: Dictionary of country data keyed by ISO3
    """

    logger.info(f"Writing {len(countries)} country JSON files")

    for iso3, data in countries.items():
        file_path = COUNTRIES_DIR / f"{iso3}.json"
        dump_to_file(data, file_path)

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
        dump_to_file(data, file_path)

    logger.info(f"Continent JSON files written to {CONTINENTS_DIR}")


def write_summary_json(
    countries: Dict[str, Dict],
    continents: Dict[str, Dict],
    total_pages: int = 0,
    not_matched: int = 0,
) -> None:
    """
    Write global summary JSON file including countries and continents.

    Args:
        countries: Dictionary of country data keyed by ISO3
        continents: Dictionary of continent data keyed by continent name
    """
    summary = {
        "files": {
            "total": total_pages,
            "matched": not_matched,
            "not_matched": total_pages - not_matched,
        },
        "countries": [],
        "continents": [],
    }

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

    dump_to_file(summary, SUMMARY_FILE)

    if SUMMARY_FILE_BACKUP:
        file_path = Path(SUMMARY_FILE_BACKUP)
        logger.info(f"Writing summary JSON backup to {file_path}")
        dump_to_file(summary, file_path)

    logger.info(f"Summary JSON written to {SUMMARY_FILE}")


def write_not_matched_files(not_matched: List[str] | Dict[str, List[str]]) -> None:
    """
    Write a text file listing files that could not be matched.

    Args:
        not_matched: List of file titles that were not matched
    """
    if not not_matched:
        logger.info("No unmatched files to write.")
        return

    not_matched_file = OUTPUT_DIR / "not_matched_files.json"
    dump_to_file(not_matched, not_matched_file)

    logger.info(f"Unmatched files written to {not_matched_file}")


def save_category_members(data: list[str]) -> None:
    """ """
    file_path = OUTPUT_DIR / "category_members.json"

    logger.info(f"Writing {len(data)} files into category_members.json")
    dump_to_file(data, file_path)


def load_category_members_from_json() -> list[str]:
    """ """
    file_path = OUTPUT_DIR / "category_members.json"
    logger.info("loading data files from category_members.json")

    if not file_path.exists():
        logger.info(f"{file_path} does not exist")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        logger.error(f"Failed to load category members from {file_path}: {e}")

    return []


__all__ = [
    "write_country_json_files",
    "write_continent_json_files",
    "write_summary_json",
    "write_not_matched_files",
    "save_category_members",
]
