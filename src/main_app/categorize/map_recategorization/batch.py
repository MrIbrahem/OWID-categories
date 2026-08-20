"""Batch orchestration for source categories in the OWID map migration."""

from __future__ import annotations

import logging

import mwclient

from ...api_services import get_category_members_titles
from .commons import recategorize_file_page
from .definitions import SOURCE_CATEGORIES
from .wikitext import normalize_region

logger = logging.getLogger(__name__)


def recategorize_source_category(
    site: mwclient.Site,
    source_region: str,
    dry_run: bool = False,
    max_items: int | None = None,
) -> dict[str, int]:
    """Process all eligible files in one broad OWID map source category."""
    region = normalize_region(source_region)
    if region is None:
        raise ValueError(f"Unsupported source region: {source_region}")

    source_category = SOURCE_CATEGORIES[region]
    titles = get_category_members_titles(site, source_category, namespace=6, max_items=max_items)
    stats = {"scanned": 0, "recategorized": 0, "skipped": 0, "errors": 0}
    category_cache: set[str] = set()

    for title in titles:
        stats["scanned"] += 1
        outcome, reason = recategorize_file_page(
            site,
            title,
            region,
            dry_run=dry_run,
            category_cache=category_cache,
        )
        if outcome == "recategorized":
            stats["recategorized"] += 1
        elif outcome == "skipped":
            stats["skipped"] += 1
            logger.info("Skipped %s: %s", title, reason)
        else:
            stats["errors"] += 1
            logger.error("Failed %s: %s", title, reason)

    return stats


__all__ = ["recategorize_source_category"]
