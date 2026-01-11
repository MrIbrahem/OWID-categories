"""
Categorization utilities for OWID Commons files.

This package contains modules for adding categories to OWID files on Wikimedia Commons.
"""

from .wiki import (
    connect_to_commons,
    add_category_to_page,
    ensure_category_exists,
    get_category_member_count,
    get_page_text,
    category_exists_on_page,
    get_category_members,
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
    "category_exists_on_page",
    # Utility functions
    "get_category_members_petscan",
    "get_category_members",
    "fetch_category_members",
]
