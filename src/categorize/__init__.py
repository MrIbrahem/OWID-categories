"""
Categorization utilities for OWID Commons files.

This package contains modules for adding categories to OWID files on Wikimedia Commons.
"""

from .wiki import (
    connect_to_commons,
    ensure_category_exists,
    get_category_member_count,
    get_page_text,
    get_category_members,
    save_page,
)

from .category_redirects import (
    add_category_to_page,
    resolve_category_redirect,
    get_redirect_target,
)

from .wikitext_utils import (
    category_exists_on_page,
    extract_redirect_target,
)

from .category_members import (
    get_category_members_petscan,
    fetch_category_members,
)

__all__ = [
    # Wiki functions
    "connect_to_commons",
    "add_category_to_page",
    "ensure_category_exists",
    "get_category_member_count",
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
]
