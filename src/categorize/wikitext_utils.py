"""
Wikitext analysis utilities for OWID Commons categorization.

This module contains functions for parsing and analyzing wikitext from Wikimedia Commons,
separating text processing from API operations.
"""

import logging
import re
from typing import Optional

import wikitextparser as wtp

logger = logging.getLogger(__name__)


def extract_redirect_target(page_text: str) -> Optional[str]:
    """
    Extract the redirect target from page text if it contains a category redirect template.

    Args:
        page_text: Wikitext of the page

    Returns:
        Target category name or None if no redirect found
    """
    if not page_text:
        return None

    parsed = wtp.parse(page_text)
    redirect_templates = {
        "category redirect",
        "categoryredirect",
        "cat redirect",
        "catredirect",
    }

    for template in parsed.templates:
        name = template.normal_name().lower().strip()
        if name in redirect_templates:
            arg = template.get_arg("1")
            if arg and arg.value:
                return arg.value.strip()
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

    category_simple = category.replace("Category:", "")

    # Match [[Category:Name]] or [[Category:Name|sortkey]] with case-insensitive "Category:"
    pattern = rf"\[\[\s*[Cc]ategory\s*:\s*{re.escape(category_simple)}\s*(?:\|[^\]]*)?]]"
    return bool(re.search(pattern, page_text))
