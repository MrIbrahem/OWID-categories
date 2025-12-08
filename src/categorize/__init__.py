"""
Categorization utilities for OWID Commons files.

This package contains modules for adding categories to OWID files on Wikimedia Commons.
"""

from .wiki import (
    connect_to_commons,
    load_credentials,
    add_category_to_page,
    ensure_category_exists,
    get_category_member_count,
    get_page_text,
    category_exists_on_page,
)

from .utils import (
    setup_logging,
    load_json_file,
    normalize_country_name,
    build_category_name,
)

__all__ = [
    # Wiki functions
    "connect_to_commons",
    "load_credentials",
    "add_category_to_page",
    "ensure_category_exists",
    "get_category_member_count",
    "get_page_text",
    "category_exists_on_page",
    # Utility functions
    "setup_logging",
    "load_json_file",
    "normalize_country_name",
    "build_category_name",
]
