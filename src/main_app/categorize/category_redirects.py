"""
Orchestration module for category redirect resolution and management.

This module coordinates API operations from wiki.py and wikitext analysis
from wikitext_utils.py to handle category redirects and page updates.
"""

import logging
import time
from typing import Optional

import mwclient

from ..api_services import MwClientPage
from . import wikitext_utils

logger = logging.getLogger(__name__)


def get_redirect_target(
    site: mwclient.Site,
    category: str,
) -> Optional[str]:
    """
    Get the redirect target for a category if it exists.

    Args:
        site: Connected mwclient Site
        category: Category name

    Returns:
        Redirect target with 'Category:' prefix, or None if no redirect
    """
    page = MwClientPage(category, site)
    page_text = page.get_text()
    if page_text is None:
        return None

    target = wikitext_utils.extract_redirect_target(page_text)
    if target:
        if not target.startswith("Category:"):
            target = f"Category:{target}"
        return target
    return None


def resolve_category_redirect(
    site: mwclient.Site,
    category: str,
    max_depth: int = 5,
) -> str:
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

    target = get_redirect_target(site, category)

    if target and target != category:
        logger.info(f"Category redirect found: {category} -> {target}")
        # Pause before recursive call
        time.sleep(1)
        return resolve_category_redirect(site, target, max_depth - 1)

    return category


def add_category_to_page(
    site: mwclient.Site,
    title: str,
    category: str,
    dry_run: bool = False,
) -> bool:
    """
    Add a category to a page on Commons.

    Args:
        site: Connected mwclient Site
        title: Page title
        category: Category to add
        dry_run: If True, don't actually make the edit

    Returns:
        True if category was added (or would be added in dry-run), False otherwise
    """
    # Get current page text via wiki module
    page = MwClientPage(title, site)
    current_text = page.get_text()

    if current_text is None:
        logger.warning(f"Page does not exist or could not be retrieved: {title}")
        return False

    # Check if category already exists via wikitext_utils
    if wikitext_utils.category_exists_on_page(current_text, category):
        logger.info(f"Category already exists on {title}")
        return False

    # Add category at the end of the page
    new_text = current_text.rstrip() + f"\n[[{category}]]\n"

    if dry_run:
        logger.info(f"[DRY RUN] Would add '{category}' to {title}")
        return True

    # Make the edit via wiki module
    edit_summary = f"Adding [[:{category}]]"

    save = page.edit(new_text, edit_summary)
    result = save.get("success") is True
    logger.info(f"Save: Success:{result} {title}")
    return result


__all__ = [
    "get_redirect_target",
    "resolve_category_redirect",
    "add_category_to_page",
]
