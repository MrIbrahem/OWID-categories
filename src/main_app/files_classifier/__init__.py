#!/usr/bin/env python3
""" """

import logging
import re
from typing import Dict, Optional, Tuple

from ..owid_country_codes import get_iso3_from_country
from ..utils import normalize_title

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

CONTINENTS_STR = "(Africa|Antarctica|Asia|Europe|North America|South America|Oceania|Americas|World)"

DATE_FORMAT = r"\d+|\w\w\w \d+,\s* \d+|[\d,]+ BCE"

# Regex patterns for classification
GRAPH_PATTERN = re.compile(rf",\s*({DATE_FORMAT})\s+to\s+({DATE_FORMAT}),\s*(\w+)\.svg$")

GRAPH_PATTERN_PLAIN = re.compile(r"^File:([^,]+),\s*([a-zA-Z]{3})\.svg$")

# Map pattern: country/region name followed by a single year
# The region/country name should start with a letter and can contain letters, spaces, hyphens, and parentheses
# Note: Hyphen is at the end of character class to avoid being interpreted as a range

MAP_PATTERN_FULL = re.compile(rf",\s*([A-Z][A-Za-z \(\)-]+),\s*({DATE_FORMAT})(?: \(cropped\))?\.svg$")

def extract_indicator(base_name: str) -> str:
    first_comma = base_name.find(",")
    indicator = base_name[:first_comma].strip() if first_comma != -1 else base_name
    return indicator


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
    graph_match_plain = GRAPH_PATTERN_PLAIN.search(title)

    if graph_match:
        _, _, iso3 = graph_match.groups()

        # Extract indicator (everything before the first comma in the normalized name)
        base_name = normalize_title(title)
        indicator = extract_indicator(base_name)

        return "graph", {
            "iso3": iso3,
            "indicator": indicator,
        }

    if graph_match_plain:
        indicator, iso3 = graph_match_plain.groups()

        # Extract indicator (everything before the first comma in the normalized name)
        base_name = normalize_title(title)
        indicator = extract_indicator(base_name)

        return "graph", {
            "iso3": iso3,
            "indicator": indicator,
        }

    # Try map pattern
    map_match = MAP_PATTERN_FULL.search(title)
    if map_match:
        region, _ = map_match.groups()
        region = region.strip()

        # Extract indicator
        base_name = normalize_title(title)
        indicator = extract_indicator(base_name)

        # Check if region is a continent
        if region in CONTINENTS:
            return "continent_map", {
                "continent": region,
                "indicator": indicator,
            }

        # Try to resolve region to ISO3
        iso3 = get_iso3_from_country(region)

        return "map", {
            "iso3": iso3,
            "region": region,
            "indicator": indicator,
        }
    # Unknown file type
    return None, None


__all__ = [
    "classify_and_parse_file",
]
