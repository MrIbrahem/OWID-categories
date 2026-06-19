#!/usr/bin/env python3
"""
Wiki API functions for OWID Commons categorization.

This module contains functions for interacting with Wikimedia Commons API,
including authentication, page editing, and category management.
"""

import logging
import time
from typing import Optional

import mwclient

logger = logging.getLogger(__name__)

# User-Agent header (required by Wikimedia)
USER_AGENT = "OWID-Commons-Categorizer/1.0 (https://github.com/MrIbrahem/OWID-categories; contact via GitHub)"

# Rate limiting: delay between edits in seconds
EDIT_DELAY = 1


def connect_to_commons(username: str, password: str) -> Optional[mwclient.Site]:
    """
    Connect to Wikimedia Commons using mwclient.

    Args:
        username: Bot username
        password: Bot password

    Returns:
        Connected Site object or None on failure
    """
    try:
        logger.info("Connecting to Wikimedia Commons...")
        site = mwclient.Site("commons.wikimedia.org", clients_useragent=USER_AGENT)

        logger.info(f"Logging in as {username}...")
        site.login(username, password)

        logger.info("Successfully connected and logged in")
        return site
    except mwclient.errors.LoginError as e:
        logger.error(f"Login failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"Failed to connect to Commons: {e}")
        return None


def get_page_text(site: mwclient.Site, title: str, max_retries: int = 3) -> Optional[str]:
    """
    Get the current text content of a page with retries and error handling.

    Args:
        site: Connected mwclient Site
        title: Page title
        max_retries: Maximum number of retries for transient errors

    Returns:
        Page text or None if page doesn't exist or on permanent failure
    """
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            page = site.pages[title]
            if page.exists:
                return page.text()
            return None
        except (mwclient.errors.MwClientError, Exception) as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1} failed to get text for '{title}': {e}. Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"Failed to get text for '{title}' after {max_retries} attempts: {e}")
    return None


def save_page(site: mwclient.Site, title: str, text: str, summary: str) -> bool:
    """
    Save wikitext to a page on Commons.

    Args:
        site: Connected mwclient Site
        title: Page title
        text: New page content
        summary: Edit summary

    Returns:
        True if successfully saved, False otherwise
    """
    try:
        page = site.pages[title]
        page.save(text, summary=summary)
        logger.info(f"Successfully saved page '{title}'")
        time.sleep(EDIT_DELAY)
        return True
    except Exception as e:
        logger.error(f"Failed to save page '{title}': {e}")
        return False


def ensure_category_exists(
    site: mwclient.Site, category_title: str, parent_category: str, sort_key: str, dry_run: bool = False
) -> bool:
    """
    Ensure the category page exists. Create it if it doesn't.

    Args:
        site: Connected mwclient Site
        category_title: Full category title (e.g., "Category:Our World in Data graphs of Canada")
        parent_category: Parent category name (e.g., "Our World in Data graphs by country")
        sort_key: Sort key for the parent category (e.g., "Canada")
        dry_run: If True, don't actually make the edit

    Returns:
        True if category exists or was created, False on error
    """
    category_page = site.pages[category_title]

    if category_page.exists:
        logger.debug(f"Category already exists: {category_title}")
        return True  # Category already exists

    # Category doesn't exist, create it
    category_content = f"[[Category:{parent_category}|{sort_key}]]"

    if dry_run:
        logger.info(f"[DRY RUN] Would create category page: {category_title}")
        return True

    # Create the category page
    edit_summary = "Create category for OWID graphs"
    return save_page(site, category_title, category_content, edit_summary)


def get_category_members(site: mwclient.Site, category: str, namespace: int | None = None) -> list:
    """
    Get all member pages in a category.

    Args:
        site: Connected mwclient Site
        category: Category name (e.g., "Category:Our World in Data graphs of Canada")
        namespace: Namespace to filter by (e.g., 6 for File)

    Returns:
        List of Page objects (empty list if category doesn't exist)
    """
    try:
        # mwclient handles the "Category:" prefix automatically.
        category_page = site.pages[category]

        if not category_page.exists:
            logger.debug(f"Category doesn't exist yet: {category}")
            return []

        return list(category_page.members(api_chunk_size=5000, namespace=namespace))

    except mwclient.errors.MwClientError as e:
        logger.error(f"API error getting members in category '{category}': {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred getting members in category '{category}': {e}")
        return []


def get_category_member_count(site: mwclient.Site, category: str) -> int:
    """
    Get the number of files currently in a category.

    Args:
        site: Connected mwclient Site
        category: Category name (e.g., "Category:Our World in Data graphs of Canada")

    Returns:
        Number of members in the category (0 if category doesn't exist)
    """
    member_count = sum(1 for _ in get_category_members(site, category))

    logger.debug(f"Category '{category}' has {member_count} members")
    return member_count
