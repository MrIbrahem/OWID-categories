#!/usr/bin/env python3
"""
OWID Commons File Fetcher and Processor
"""

import logging
import time

import mwclient
import requests
from mwclient.client import Site

logger = logging.getLogger(__name__)

# Configuration
API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"


def get_category_count(category_name):
    # Ensure the title has the proper prefix
    if not category_name.startswith("Category:"):
        category_name = f"Category:{category_name}"

    url = API_ENDPOINT
    params = {"action": "query", "titles": category_name, "prop": "categoryinfo", "format": "json"}

    # Always include a descriptive User-Agent header per Wikipedia API guidelines
    headers = {"User-Agent": "CategoryCounterBot/1.0 (your_email@example.com)"}

    response = requests.get(url, params=params, headers=headers).json()

    # Extract the page data dynamically since the page ID string changes
    pages = response.get("query", {}).get("pages", {})
    page_id = list(pages.keys())[0]

    info = pages[page_id].get("categoryinfo", {})
    # {'size': 354, 'pages': 1, 'files': 309, 'subcats': 44}
    size = info.get("size") or 0
    return size


def get_category_members_titles(
    site: Site,
    category_name: str,
    namespace: int | None = None,
) -> list[str]:
    """
    Fetch all file titles from the OWID category using MediaWiki API with pagination.

    Returns:
        List of file titles (strings).
    """
    page_count = 0
    delay = 0.1  # seconds
    max_delay = 8.0

    logger.info(f"Starting to fetch files from {category_name}")

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
    first_request = True
    cmcontinue = None
    while first_request or cmcontinue is not None:
        first_request = False
        if len(all_files) % 1000 == 0:
            logger.info(f"loaded {len(all_files)} members")

        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        try:
            data = site.get("query", **params)
            members = data.get("query", {}).get("categorymembers", [])
            all_files.extend([x.get("title", "") for x in members])
            page_count += 1

            logger.debug(f"Fetched category members {page_count}: {len(members)} page, (total: {len(all_files)})")

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
            if delay < max_delay:
                delay = min(delay * 2, max_delay)
                time.sleep(delay)
                continue

    logger.info(f"Finished fetching {len(all_files)} files in {page_count} pages")
    return all_files


def get_category_members(
    site: Site,
    category_title: str,
    namespace: int | None = None,
) -> list[str]:
    """
    Retrieve all members of a specified category from a MediaWiki site.
    """
    logger.debug(f"load category members for {category_title}")
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


__all__ = [
    "get_category_count",
    "get_category_members_titles",
    "get_category_members",
]
