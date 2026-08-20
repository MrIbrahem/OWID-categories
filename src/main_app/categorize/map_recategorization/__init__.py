"""OWID map recategorization package.

The package preserves the original import surface while separating static
configuration, pure wikitext transformations, Commons operations, and batch
orchestration into focused modules.
"""

from .batch import recategorize_source_category
from .commons import ensure_map_category_exists, recategorize_file_page
from .definitions import (
    CATEGORY_DESCRIPTION_TEMPLATE,
    REGION_ALIASES,
    SOURCE_CATEGORIES,
    TOPIC_PARENT_CATEGORY,
)
from .models import MapRecategorization, WikitextRewrite
from .wikitext import normalize_region, rewrite_map_page

__all__ = [
    "CATEGORY_DESCRIPTION_TEMPLATE",
    "REGION_ALIASES",
    "SOURCE_CATEGORIES",
    "TOPIC_PARENT_CATEGORY",
    "MapRecategorization",
    "WikitextRewrite",
    "ensure_map_category_exists",
    "normalize_region",
    "recategorize_file_page",
    "recategorize_source_category",
    "rewrite_map_page",
]
