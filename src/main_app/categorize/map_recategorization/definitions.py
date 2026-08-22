"""Static definitions for the OWID map recategorization domain."""

CATEGORY_DESCRIPTION_TEMPLATE = "{{Category description/Our World in Data maps by continent and year}}"
TOPIC_PARENT_CATEGORY = "[[Category:Our World in Data maps by topic]]"

# Canonical labels are used in destination categories. Historical aliases are
# accepted while reading standardized names that have already been uploaded.
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

__all__ = [
    "CATEGORY_DESCRIPTION_TEMPLATE",
    "REGION_ALIASES",
    "SOURCE_CATEGORIES",
    "TOPIC_PARENT_CATEGORY",
]
