#!/usr/bin/env python3
"""
Wiki API functions for OWID Commons categorization.

This module contains functions for interacting with Wikimedia Commons API,
including authentication, page editing, and category management.
"""

import logging
import os
from typing import Optional

import mwclient
from dotenv import load_dotenv


# User-Agent header (required by Wikimedia)
USER_AGENT = "OWID-Commons-Categorizer/1.0 (https://github.com/MrIbrahem/OWID-categories; contact via GitHub)"

# Rate limiting: delay between edits in seconds
EDIT_DELAY = 0.1


def load_credentials() -> tuple[Optional[str], Optional[str]]:
    """
    Load credentials from .env file.

    Returns:
        Tuple of (username, password) or (None, None) if not found
    """
    load_dotenv()
    username = os.getenv("WM_USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        logging.error("WM_USERNAME and/or PASSWORD not found in .env file")
        return None, None

    return username, password


def connect_to_commons(username: str, password: str) -> Optional[mwclient.Site]:
    """
    Connect to Wikimedia Commons using mwclient.

    Args:
        username: Bot username
        password: Bot password

    Returns:
        Connected Site object or None on failure
    """
    logging.info("Connecting to Wikimedia Commons...")
    site = mwclient.Site("commons.wikimedia.org", clients_useragent=USER_AGENT)

    logging.info(f"Logging in as {username}...")
    site.login(username, password)

    logging.info("Successfully connected and logged in")
    return site


def get_page_text(site: mwclient.Site, title: str) -> Optional[str]:
    """
    Get the current text content of a page.

    Args:
        site: Connected mwclient Site
        title: Page title

    Returns:
        Page text or None if page doesn't exist
    """
    page = site.pages[title]
    if page.exists:
        return page.text()
    return None


def category_exists_on_page(page_text: str, category: str) -> bool:
    """
    Check if a category already exists on a page.

    Args:
        page_text: Current page text
        category: Category name to check (e.g., "Category:Our World in Data graphs of Canada")

    Returns:
        True if category exists, False otherwise
    """
    if not page_text:
        return False

    # Check for various category formats
    # [[Category:Name]] or [[category:Name]]
    category_simple = category.replace("Category:", "")

    checks = [
        f"[[{category}]]",
        f"[[{category.lower()}]]",
        f"[[Category:{category_simple}]]",
        f"[[category:{category_simple}]]",
    ]

    return any(check in page_text for check in checks)


def add_category_to_page(
    site: mwclient.Site,
    title: str,
    category: str,
    dry_run: bool = False
) -> bool:
    """
    Add a category to a page on Commons.

    Args:
        site: Connected mwclient Site
        title: Page title (e.g., "File:Agriculture share gdp, 1997 to 2021, CAN.svg")
        category: Category to add (e.g., "Category:Our World in Data graphs of Canada")
        dry_run: If True, don't actually make the edit

    Returns:
        True if category was added (or would be added in dry-run), False otherwise
    """
    page = site.pages[title]

    if not page.exists:
        logging.warning(f"Page does not exist: {title}")
        return False

    # Get current page text
    current_text = page.text()

    # Check if category already exists
    if category_exists_on_page(current_text, category):
        logging.info(f"Category already exists on {title}")
        return False

    # Add category at the end of the page
    new_text = current_text.rstrip() + f"\n[[{category}]]\n"

    if dry_run:
        logging.info(f"[DRY RUN] Would add '{category}' to {title}")
        return True

    # Make the edit
    edit_summary = f"Add {category}"
    page.save(new_text, summary=edit_summary)

    logging.info(f"Successfully added '{category}' to {title}")
    return True


def ensure_category_exists(
    site: mwclient.Site,
    category_title: str,
    parent_category: str,
    sort_key: str,
    dry_run: bool = False
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
        logging.debug(f"Category already exists: {category_title}")
        return True    # Category doesn't exist, create it
    category_content = f"[[Category:{parent_category}|{sort_key}]]"

    if dry_run:
        logging.info(f"[DRY RUN] Would create category page: {category_title}")
        return True

    # Create the category page
    edit_summary = "Create category for OWID graphs"
    category_page.save(category_content, summary=edit_summary)

    logging.info(f"Created category page: {category_title}")
    return True


def get_category_member_count(site: mwclient.Site, category: str) -> int:
    """
    Get the number of files currently in a category.

    Args:
        site: Connected mwclient Site
        category: Category name (e.g., "Category:Our World in Data graphs of Canada")

    Returns:
        Number of members in the category (0 if category doesn't exist)
    """
    try:
        # Remove "Category:" prefix if present for the API call
        category_name = category.replace("Category:", "")

        # Get the category page
        category_page = site.pages[f"Category:{category_name}"]

        if not category_page.exists:
            logging.debug(f"Category doesn't exist yet: {category}")
            return 0

        # Count members in the category
        member_count = sum(1 for _ in category_page.members())

        logging.debug(f"Category '{category}' has {member_count} members")
        return member_count

    except Exception as e:
        logging.error(f"Error counting members in category '{category}': {e}")
        return 0


def get_edit_delay() -> float:
    """
    Get the delay between edits in seconds.

    Returns:
        Delay in seconds
    """
    return EDIT_DELAY
