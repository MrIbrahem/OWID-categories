"""
Categorization utilities for OWID Commons files.

This package contains modules for adding categories to OWID files on Wikimedia Commons.
"""

from .category_members import (
    fetch_category_members,
    get_category_count,
    get_category_members_petscan,
)
from .category_redirects import (
    add_category_to_page,
    get_redirect_target,
    resolve_category_redirect,
)
from .wiki import (
    connect_to_commons,
    ensure_category_exists,
    get_category_members,
    get_page_text,
    save_page,
)
from .wikitext_utils import (
    category_exists_on_page,
    extract_redirect_target,
)

__all__ = [
    # Wiki functions
    "connect_to_commons",
    "add_category_to_page",
    "ensure_category_exists",
    "get_page_text",
    "resolve_category_redirect",
    "category_exists_on_page",
    "save_page",
    "get_redirect_target",
    "extract_redirect_target",
    # Utility functions
    "get_category_members_petscan",
    "get_category_members",
    "fetch_category_members",
    "get_category_count",
]
