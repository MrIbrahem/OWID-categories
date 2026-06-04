#!/usr/bin/env python3
"""
Wiki API functions for OWID Commons categorization.

This module contains functions for interacting with Wikimedia Commons API,
including authentication, page editing, and category management.
"""

import logging
import time
import re
from typing import Optional
import mwclient
import wikitextparser as wtp


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
        logging.info("Connecting to Wikimedia Commons...")
        site = mwclient.Site("commons.wikimedia.org", clients_useragent=USER_AGENT)

        logging.info(f"Logging in as {username}...")
        site.login(username, password)

        logging.info("Successfully connected and logged in")
        return site
    except mwclient.errors.LoginError as e:
        logging.error(f"Login failed: {e}")
        return None
    except Exception as e:
        logging.exception(f"Failed to connect to Commons: {e}")
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
                logging.warning(f"Attempt {attempt + 1} failed to get text for '{title}': {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logging.error(f"Failed to get text for '{title}' after {max_retries} attempts: {e}")
    return None


def resolve_category_redirect(site: mwclient.Site, category: str, max_depth: int = 5) -> str:
    """
    Resolve category redirects. If the category has a {{Category redirect}} template,
    return the target category name.

    Args:
        site: Connected mwclient Site
        category: Original category name
        max_depth: Maximum recursion depth to avoid infinite loops

    Returns:
        Resolved category name
    """
    if max_depth <= 0:
        return category

    page_text = get_page_text(site, category)
    if not page_text:
        return category

    parsed = wtp.parse(page_text)
    redirect_templates = {
        "category redirect",
        "categoryredirect",
        "cat redirect",
        "catredirect",
    }

    target = None
    for template in parsed.templates:
        name = template.normal_name().lower().strip()
        if name in redirect_templates:
            arg = template.get_arg("1")
            if arg and arg.value:
                target = arg.value.strip()
                break

    if target:
        # Ensure it has Category: prefix if the match doesn't include it
        if not target.startswith("Category:"):
            target = f"Category:{target}"

        logging.info(f"Category redirect found: {category} -> {target}")
        # Pause before recursive call
        time.sleep(1)
        return resolve_category_redirect(site, target, max_depth - 1)

    return category


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

    category_simple = category.replace("Category:", "")

    # Match [[Category:Name]] or [[Category:Name|sortkey]] with case-insensitive "Category:"
    pattern = rf"\[\[\s*[Cc]ategory\s*:\s*{re.escape(category_simple)}\s*(?:\|[^\]]*)?]]"
    return bool(re.search(pattern, page_text))


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
    edit_summary = f"Adding [[:{category}]]"
    try:
        page.save(new_text, summary=edit_summary)
        logging.info(f"Successfully added '{category}' to {title}")
        time.sleep(EDIT_DELAY)
        return True

    except Exception as e:
        logging.error(f"Failed to save category to {title}: {e}")
        return False


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
        return True    # Category already exists

    # Category doesn't exist, create it
    category_content = f"[[Category:{parent_category}|{sort_key}]]"

    if dry_run:
        logging.info(f"[DRY RUN] Would create category page: {category_title}")
        return True

    # Create the category page
    edit_summary = "Create category for OWID graphs"

    try:
        category_page.save(category_content, summary=edit_summary)
        logging.info(f"Created category page: {category_title}")
        return True
    except Exception as e:
        logging.error(f"Failed to create category page '{category_title}': {e}")
        return False


def get_category_members(site: mwclient.Site, category: str) -> list:
    """
    Get all member pages in a category.

    Args:
        site: Connected mwclient Site
        category: Category name (e.g., "Category:Our World in Data graphs of Canada")

    Returns:
        List of Page objects (empty list if category doesn't exist)
    """
    try:
        # mwclient handles the "Category:" prefix automatically.
        category_page = site.pages[category]

        if not category_page.exists:
            logging.debug(f"Category doesn't exist yet: {category}")
            return []

        return list(category_page.members())

    except mwclient.errors.MwClientError as e:
        logging.error(f"API error getting members in category '{category}': {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred getting members in category '{category}': {e}")
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

    logging.debug(f"Category '{category}' has {member_count} members")
    return member_count
