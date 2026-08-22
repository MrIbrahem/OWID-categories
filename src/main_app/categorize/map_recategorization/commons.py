"""Commons page and category operations for OWID map recategorization."""

from __future__ import annotations

import logging

import mwclient

from ...api_services import MwClientPage
from .definitions import CATEGORY_DESCRIPTION_TEMPLATE, TOPIC_PARENT_CATEGORY
from .wikitext import rewrite_map_page

logger = logging.getLogger(__name__)


def ensure_map_category_exists(
    site: mwclient.Site,
    category: str,
    content: str,
    dry_run: bool = False,
) -> bool:
    """Create a destination category with its mandated content when absent."""
    page = MwClientPage(category, site)
    if page.exists():
        return True
    if dry_run:
        logger.info("[DRY RUN] Would create category page: %s", category)
        return True

    result = page.create(content, "Create category for OWID map recategorization")
    if not result.get("success"):
        logger.error("Failed to create category %s: %s", category, result)
        return False
    return True


def recategorize_file_page(
    site: mwclient.Site,
    title: str,
    source_region: str,
    dry_run: bool = False,
    category_cache: set[str] | None = None,
) -> tuple[str, str | None]:
    """Recategorize one file page and return ``(outcome, reason)``.

    Outcomes are ``recategorized``, ``skipped`` and ``error``. All category
    creation and file-page changes are skipped in dry-run mode.
    """
    page = MwClientPage(title, site)
    current_text = page.get_text()
    if current_text is None:
        return "error", "page text could not be retrieved"

    rewrite = rewrite_map_page(title, current_text, source_region)
    if not rewrite.changed or rewrite.change is None:
        return "skipped", rewrite.reason

    cache = category_cache if category_cache is not None else set()
    category_contents = {
        rewrite.change.location_year_category: CATEGORY_DESCRIPTION_TEMPLATE,
        rewrite.change.topic_category: TOPIC_PARENT_CATEGORY,
    }
    for category, content in category_contents.items():
        if category in cache:
            continue
        if not ensure_map_category_exists(site, category, content, dry_run=dry_run):
            return "error", f"could not ensure category: {category}"
        cache.add(category)

    if dry_run:
        logger.info("[DRY RUN] Would recategorize %s", title)
        return "recategorized", None

    summary = (
        "Recategorize OWID map by location, year, and topic "
        f"([[:{rewrite.change.location_year_category}]]; [[:{rewrite.change.topic_category}]])"
    )
    result = page.edit(rewrite.text, summary)
    if not result.get("success"):
        logger.error("Failed to recategorize %s: %s", title, result)
        return "error", str(result.get("error", "edit failed"))
    return "recategorized", None


__all__ = ["ensure_map_category_exists", "recategorize_file_page"]
