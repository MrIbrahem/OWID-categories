#!/usr/bin/env python3
"""
Wiki API functions for OWID Commons categorization.

This module contains functions for interacting with Wikimedia Commons API,
including authentication, page editing, and category management.
"""

import logging
from typing import Optional

import mwclient
from mwclient import Site

from ..api_services import MwClientPage

logger = logging.getLogger(__name__)

# User-Agent header (required by Wikimedia)
USER_AGENT = "OWID-Commons-Categorizer/1.0 (https://github.com/MrIbrahem/OWID-categories; contact via GitHub)"

# Rate limiting: delay between edits in seconds
EDIT_DELAY = 1


def connect_to_commons(username: str, password: str) -> Optional[Site]:
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
        site = Site("commons.wikimedia.org", clients_useragent=USER_AGENT)

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


def ensure_category_exists(
    site: Site,
    category_title: str,
    parent_category: str,
    sort_key: str,
    dry_run: bool = False,
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

    category_page = MwClientPage(category_title, site)

    if category_page.exists():
        logger.debug(f"Category already exists: {category_title}")
        return True  # Category already exists

    # Category doesn't exist, create it
    category_content = f"[[Category:{parent_category}|{sort_key}]]"

    if dry_run:
        logger.info(f"[DRY RUN] Would create category page: {category_title}")
        return True

    # Create the category page
    edit_summary = "Create category for OWID graphs"

    save = category_page.edit(category_content, edit_summary)
    return save.get("success") is True
