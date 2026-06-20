""" """

import logging
from typing import Any

from ..api_services import get_category_count
from ..api_services.category_members import get_subcats_informations
from ..utils import build_category_name

logger = logging.getLogger(__name__)

# get_category_count("Category:Our_World_in_Data_maps_of_the_world")
# get_subcats_informations(site, "Category:Our_World_in_Data_graphs_by_country")
# get_subcats_informations(site, "Category:Our_World_in_Data_maps_by_continent")


def countries_categories_data(site):
    data = get_subcats_informations(site, "Category:Our_World_in_Data_graphs_by_country")
    return {x: v["files"] for x, v in data.items()}


def continents_categories_data(site):
    data = get_subcats_informations(site, "Category:Our_World_in_Data_maps_by_continent")
    return {x: v["files"] for x, v in data.items()}


def make_report_data(
    site: Any,
    countries: dict[str, dict],
    continents: dict[str, dict],
) -> dict:
    continents_real = continents_categories_data(site)
    countries_real = countries_categories_data(site)
    world_category = "Category:Our World in Data maps of the world"

    continents_data = {
        world_category: {"new": 0, "count": 0},
    }

    for continent, data in continents.items():
        category = f"Category:Our World in Data maps of {continent}"

        if continent == "World":
            category = world_category

        continents_data[category] = {
            "new": len(data["maps"]),
            "count": continents_real.get(category) or 0,
        }

    continents_data[world_category]["count"] = get_category_count(world_category)

    countries_data = {}

    for _, data in countries.items():
        country = data["country"]
        len_graphs = len(data["graphs"])
        category = build_category_name(country)
        countries_data[category] = {"new": len_graphs, "count": countries_real.get(category) or 0}

    return {
        "continents": continents_data,
        "countries": countries_data,
    }


def create_wikitext_report(
    data: dict[str, dict],
) -> str:
    """ """
    text = ""
    return text


__all__ = [
    "make_report_data",
    "create_wikitext_report",
]
