"""Wikitext transformation and Commons operations for OWID map recategorization.

The workflow moves files out of the broad OWID map categories only when the
file page contains ``{{Map showing old data|year=...}}``.  Each eligible file
gets a location/year category and a topic category, while the legacy marker
and broad categories are removed in one edit.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass

import mwclient

from ..api_services import MwClientPage, get_category_members_titles

logger = logging.getLogger(__name__)

CATEGORY_DESCRIPTION_TEMPLATE = "{{Category description/Our World in Data maps by continent and year}}"
TOPIC_PARENT_CATEGORY = "[[Category:Our World in Data maps by topic]]"

# The canonical labels are used in every destination category.  The aliases
# accept the standardized variants already present in historical file names.
REGION_ALIASES: dict[str, tuple[str, ...]] = {
    "Africa": ("Africa",),
    "Asia": ("Asia",),
    "Europe": ("Europe",),
    "North America": ("North America", "NorthAmerica"),
    "South America": ("South America", "SouthAmerica"),
    "Oceania": ("Oceania",),
    "the world": ("World", "the world"),
}

SOURCE_CATEGORIES: dict[str, str] = {
    region: f"Category:Our World in Data maps of {region}" for region in REGION_ALIASES
}

_MAP_SHOWING_OLD_DATA_RE = re.compile(
    r"\{\{\s*Map\s+showing\s+old\s+data\s*\|\s*year\s*=\s*(?P<year>[^|}\n]+?)\s*\}\}",
    re.IGNORECASE,
)
_CATEGORY_LINK_RE = re.compile(r"\[\[\s*Category\s*:\s*(?P<name>[^\]|]+)(?:\|[^\]]*)?\]\]", re.IGNORECASE)


@dataclass(frozen=True)
class MapRecategorization:
    """The categories and normalized metadata derived from an eligible map."""

    region: str
    year: str
    topic: str

    @property
    def location_year_category(self) -> str:
        return f"Category:Our World in Data maps of {self.region} showing {self.year} data"

    @property
    def topic_category(self) -> str:
        return f"Category:Our World in Data maps showing {self.topic}"


@dataclass(frozen=True)
class WikitextRewrite:
    """Result of evaluating one Commons file page."""

    change: MapRecategorization | None
    text: str
    reason: str | None = None

    @property
    def changed(self) -> bool:
        return self.change is not None


def normalize_region(region: str) -> str | None:
    """Return a canonical OWID map region label for a historical alias."""
    candidate = re.sub(r"\s+", " ", region.strip()).casefold()
    for canonical, aliases in REGION_ALIASES.items():
        if any(candidate == re.sub(r"\s+", " ", alias).casefold() for alias in aliases):
            return canonical
    return None


def _extract_topic(title: str, region: str, year: str) -> str | None:
    """Extract the topic before the terminal `, region, year.svg` portion."""
    name = title.strip()
    if name.casefold().startswith("file:"):
        name = name[5:]

    aliases = REGION_ALIASES[region]
    alias_pattern = "|".join(re.escape(alias).replace(r"\\ ", r"\\s*") for alias in aliases)
    pattern = re.compile(
        rf"^(?P<topic>.+?),\s*(?:{alias_pattern})\s*,\s*{re.escape(year)}(?:\s*\(cropped\))?\.svg$",
        re.IGNORECASE,
    )
    match = pattern.match(name)
    if not match:
        return None

    topic = match.group("topic").strip()
    if not topic or "[[" in topic or "]]" in topic:
        return None
    return topic


def _normalized_category_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.replace("_", " ").strip()).casefold()


def _is_legacy_category(category_name: str, region: str, year: str) -> bool:
    """Identify the two source-category forms that must be removed."""
    expected_names = {f"{year} maps of {alias}" for alias in REGION_ALIASES[region]}
    expected_names.update(f"Our World in Data maps of {alias}" for alias in REGION_ALIASES[region])
    normalized = _normalized_category_name(category_name)
    return any(normalized == _normalized_category_name(expected) for expected in expected_names)


def _remove_legacy_categories(text: str, region: str, year: str) -> str:
    def replacement(match: re.Match[str]) -> str:
        return "" if _is_legacy_category(match.group("name"), region, year) else match.group(0)

    return _CATEGORY_LINK_RE.sub(replacement, text)


def _append_missing_categories(text: str, categories: Iterable[str]) -> str:
    existing = {_normalized_category_name(match.group("name")) for match in _CATEGORY_LINK_RE.finditer(text)}
    missing = [category for category in categories if _normalized_category_name(category[9:]) not in existing]
    if not missing:
        return text
    return text.rstrip() + "\n" + "\n".join(f"[[{category}]]" for category in missing) + "\n"


def rewrite_map_page(title: str, text: str, source_region: str) -> WikitextRewrite:
    """Build the one-edit wikitext replacement for a source-category file.

    Files without the old-data template are intentionally left untouched.  A
    mismatched filename is also left untouched so an operator can review it,
    rather than introducing a malformed topic category.
    """
    region = normalize_region(source_region)
    if region is None:
        return WikitextRewrite(change=None, text=text, reason="unsupported source region")

    template_matches = list(_MAP_SHOWING_OLD_DATA_RE.finditer(text))
    if not template_matches:
        return WikitextRewrite(change=None, text=text, reason="no old-data template")

    years = {match.group("year").strip() for match in template_matches}
    if len(years) != 1:
        return WikitextRewrite(change=None, text=text, reason="ambiguous old-data years")

    year = years.pop()
    topic = _extract_topic(title, region, year)
    if topic is None:
        return WikitextRewrite(change=None, text=text, reason="filename does not match the expected map format")

    change = MapRecategorization(region=region, year=year, topic=topic)
    new_text = _MAP_SHOWING_OLD_DATA_RE.sub("", text)
    new_text = _remove_legacy_categories(new_text, region, year)
    new_text = _append_missing_categories(new_text, (change.location_year_category, change.topic_category))

    if new_text == text:
        return WikitextRewrite(change=None, text=text, reason="already recategorized")
    return WikitextRewrite(change=change, text=new_text)


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

    Outcomes are ``recategorized``, ``skipped`` and ``error``.  All category
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
