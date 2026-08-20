#!/usr/bin/env python3
"""
OWID Commons File Fetcher and Processor
"""

import logging
import time
from typing import Any

import mwclient
import requests
from mwclient.client import Site
from tqdm import tqdm

from ..owid_config import USER_AGENT

logger = logging.getLogger(__name__)

# Configuration
API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"


def get_category_count(category_name: str) -> int:
    # Ensure the title has the proper prefix
    if not category_name.startswith("Category:"):
        category_name = f"Category:{category_name}"

    url = API_ENDPOINT
    params = {
        "action": "query",
        "format": "json",
        "prop": "categoryinfo",
        "titles": category_name,
        "utf8": 1,
        "formatversion": "2",
    }

    # Always include a descriptive User-Agent header per Wikipedia API guidelines
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        logger.error(f"Failed to fetch category info for {category_name}: {e}")
        return 0
    # { "batchcomplete": true, "query": { "pages": [ { "pageid": 718741, "ns": 14, "title": "Category:Yemen", "categoryinfo": { "size": 19, "pages": 3, "files": 0, "subcats": 16, "hidden": false } } ] } }
    # Extract the page data dynamically since the page ID string changes
    pages = data.get("query", {}).get("pages", [{}])
    if not pages:
        return 0

    info = pages[0].get("categoryinfo", {})
    # {'size': 354, 'pages': 1, 'files': 309, 'subcats': 44}
    size = info.get("size") or 0
    return size


def get_category_members_titles(
    site: Site,
    category_name: str,
    namespace: int | None = None,
    total_pages: int | None = None,
    max_items: int | None = None,
) -> list[str]:
    """
    Fetch all file titles from the OWID category using MediaWiki API with pagination.

    Returns:
        List of file titles (strings).
    """
    delay = 0.1  # seconds
    max_delay = 8.0

    total_pages = max_items or total_pages or get_category_count(category_name)
    logger.info(f"Starting to fetch files from {category_name}, total members: {total_pages}")

    params = {
        # "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category_name,
        # "cmtype": "file",
        "cmlimit": "max",
    }

    if namespace is not None:
        if namespace == 14:
            params["cmtype"] = "subcat"
        elif namespace == 6:
            params["cmtype"] = "file"
        else:
            params["cmnamespace"] = str(namespace)

    all_files = []
    cmcontinue = None

    # Initialize tqdm with the total expected items
    with tqdm(total=total_pages, desc="Fetching members", unit="item") as pbar:
        while True:
            if max_items and len(all_files) >= max_items:
                break

            if cmcontinue:
                params["cmcontinue"] = cmcontinue

            try:
                data = site.get("query", **params)
                members = data.get("query", {}).get("categorymembers", [])

                # Extract titles. The API may return up to 500 entries, so trim
                # the final batch to make max_items an exact safety limit.
                new_titles = [x.get("title", "") for x in members]
                if max_items is not None:
                    remaining = max_items - len(all_files)
                    new_titles = new_titles[:remaining]
                all_files.extend(new_titles)

                # Update the progress bar by the number of items fetched in this batch
                pbar.update(len(new_titles))

                logger.debug(f"Fetched category members: {len(members)} page, (total: {len(all_files)}/{total_pages})")

                if max_items is not None and len(all_files) >= max_items:
                    break

                if "continue" in data:
                    cmcontinue = data["continue"].get("cmcontinue")
                    time.sleep(delay)
                else:
                    break

            except mwclient.errors.APIError as e:
                if e.code == "invalidcategory":
                    logger.warning(f"Invalid category: {category_name}")
                    break

            except Exception as e:
                logger.error("API request failed %s", str(e))
                if delay >= max_delay:
                    break

                time.sleep(delay)
                delay = min(delay * 2, max_delay)
                continue

    logger.info(f"Finished fetching {len(all_files)} pages.")
    return all_files


def get_category_members(
    site: Site,
    category_title: str,
    namespace: int | None = None,
) -> list[str]:
    """
    Retrieve all members of a specified category from a MediaWiki site.
    """
    logger.info(f"load category members for {category_title}")

    try:
        category = site.pages[category_title]
        # Use list comprehension for efficiency - consumes the generator
        members = category.members(  # type: ignore
            prop="ids|title",
            namespace=namespace,
            sort="sortkey",
            dir="asc",
            start=None,
            end=None,
            generator=True,
        )

        list_members = []
        for p in members:
            title = p if isinstance(p, str) else p.name

            if len(list_members) % 1000 == 0:
                logger.debug(f"loaded {len(list_members)} members")

            list_members.append(title)

        return list_members

    except mwclient.errors.APIError as e:
        logger.warning(f"API error getting category members for {category_title}: {e}")
        return []
    except KeyError as e:
        logger.warning(f"Key error in API response for {category_title}: {e}")
        return []


def get_subcats_informations(
    site: Site,
    category_name: str,
) -> dict[str, Any]:
    """ """
    logger.info(f"Starting to fetch informations of {category_name} subcats")

    params = {
        # "action": "query",
        "format": "json",
        "prop": "categoryinfo",
        "generator": "categorymembers",
        "formatversion": "2",
        "gcmtitle": category_name,
        "gcmtype": "subcat",
        "gcmlimit": "max",
    }

    data = {}

    try:
        data = site.get("query", **params)
    except mwclient.errors.APIError as e:
        if e.code == "invalidcategory":
            logger.warning(f"Invalid category: {category_name}")

    except Exception as e:
        logger.error("API request failed %s", str(e))

    pages = data.get("query", {}).get("pages", [])

    # "categoryinfo": { "size": 12, "pages": 0, "files": 12, "subcats": 0, "hidden": false }
    data = {x["title"]: x.get("categoryinfo", {}) for x in pages if x.get("title")}

    return data


__all__ = [
    "get_category_count",
    "get_category_members_titles",
    "get_category_members",
    "get_subcats_informations",
]
