#!/usr/bin/env python3
"""
OWID Commons File Fetcher and Processor
"""

import logging
import urllib
from typing import Dict, List
import requests

logger = logging.getLogger(__name__)

# Configuration
API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"

# User-Agent header (required by Wikimedia)
USER_AGENT = "OWID-Commons-Processor/1.0 (https://github.com/MrIbrahem/OWID-categories; contact via GitHub)"


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


def fetch_category_members(category_name) -> List[Dict]:
    """
    Fetch all files from the OWID category using MediaWiki API with pagination.

    Returns:
        List of file dictionaries with 'pageid', 'title', etc.
    """
    all_files = []
    cmcontinue = None
    page_count = 0

    logger.info(f"Starting to fetch files from {category_name}")

    while True:
        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": category_name,
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
