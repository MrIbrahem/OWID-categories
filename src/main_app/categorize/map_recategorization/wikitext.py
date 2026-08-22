"""Pure wikitext parsing and transformation for OWID map recategorization."""

from __future__ import annotations

import re
from collections.abc import Iterable

from .definitions import REGION_ALIASES
from .models import MapRecategorization, WikitextRewrite

_MAP_SHOWING_OLD_DATA_RE = re.compile(
    r"\{\{\s*Map\s+showing\s+old\s+data\s*\|\s*year\s*=\s*(?P<year>[^|}\n]+?)\s*\}\}",
    re.IGNORECASE,
)
_CATEGORY_LINK_RE = re.compile(r"\[\[\s*Category\s*:\s*(?P<name>[^\]|]+)(?:\|[^\]]*)?\]\]", re.IGNORECASE)


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
    alias_pattern = "|".join(re.escape(alias) for alias in aliases)
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

    Files without the old-data template are intentionally left untouched. A
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


__all__ = ["normalize_region", "rewrite_map_page"]
