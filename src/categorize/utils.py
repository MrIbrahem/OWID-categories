#!/usr/bin/env python3
"""
Utility functions for OWID Commons categorization.

This module contains helper functions for logging, data loading,
and country name normalization.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional


# Configuration
LOG_DIR = Path("logs")


def setup_logging(log_file: Path):
    """
    Set up logging configuration.

    Args:
        log_file: Path to log file
    """
    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_json_file(file_path: Path) -> Optional[Dict]:
    """
    Load a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data or None on error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return None


def normalize_country_name(country: str) -> str:
    """
    Normalize country name by adding "the" prefix where appropriate.

    According to proper English grammar, certain country names require "the" article.

    Args:
        country: Country name (e.g., "United Kingdom", "Canada")

    Returns:
        Normalized country name (e.g., "the United Kingdom", "Canada")
    """
    # Countries that require "the" prefix
    # Based on proper English usage for country names
    countries_with_the = {
        "Democratic Republic of Congo",
        "Dominican Republic",
        "Philippines",
        "Netherlands",
        "United Arab Emirates",
        "United Kingdom",
        "United States",
        "Czech Republic",
        "Central African Republic",
        "Maldives",
        "Seychelles",
        "Bahamas",
        "Marshall Islands",
        "Solomon Islands",
        "Comoros",
        "Gambia",
        "Vatican City",
        # Note: "Vatican" is included to handle the variant name used in OWID country codes,
        # even though "Vatican City" is the standard form
        "Vatican",
    }

    if country in countries_with_the:
        return f"the {country}"
    return country


def build_category_name(entity_name: str, category_type: str = "country", files_type: str = "graphs") -> str:
    """
    Build the category name for a country or continent.

    Args:
        entity_name: Entity name (e.g., "Canada", "Africa")
        category_type: Type of entity ("country" or "continent")

    Returns:
        Category name with normalized entity name
        (e.g., "Category:Our World in Data graphs of Canada",
               "Category:Our World in Data graphs of Africa")
    """
    pre_defined_categories = {
        "graphs": {
            "World": "Category:Our World in Data graphs of the world",
        },
        "maps": {
            "World": "Category:Our World in Data maps of the world",
        },
    }

    if files_type not in pre_defined_categories:
        files_type = "graphs"

    if entity_name in pre_defined_categories.get(files_type, {}):
        return pre_defined_categories[files_type][entity_name]

    if category_type == "country":
        normalized_name = normalize_country_name(entity_name)
    else:
        normalized_name = entity_name

    return f"Category:Our World in Data {files_type} of {normalized_name}"


def get_parent_category(category_type: str = "country") -> str:
    """
    Get the parent category name based on entity type.

    Args:
        category_type: Type of entity ("country" or "continent")

    Returns:
        Parent category name
    """
    if category_type == "continent":
        return "Our World in Data graphs by continent"
    return "Our World in Data graphs by country"
