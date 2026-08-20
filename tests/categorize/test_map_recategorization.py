"""Tests for the OWID continent/world map recategorization workflow."""

from unittest.mock import MagicMock, patch

import pytest

from src.main_app.api_services.category_members import get_category_members_titles
from src.main_app.categorize.map_recategorization import (
    CATEGORY_DESCRIPTION_TEMPLATE,
    TOPIC_PARENT_CATEGORY,
    normalize_region,
    recategorize_file_page,
    recategorize_source_category,
    rewrite_map_page,
)


@pytest.mark.unit
class TestMapWikitextRewriting:
    """Verify the pure, one-edit transformation before any Commons operation."""

    def test_rewrites_asia_map_and_removes_legacy_markup(self):
        original = """{{Information|description=Example}}
{{Map showing old data|year=1751}}
[[Category:1751 maps of Asia]]
[[Category:Our World in Data maps of Asia]]
[[Category:Unrelated maps]]
"""

        result = rewrite_map_page("File:Absolute change co2, Asia, 1751.svg", original, "Asia")

        assert result.changed is True
        assert result.change is not None
        assert result.change.region == "Asia"
        assert result.change.year == "1751"
        assert result.change.topic == "Absolute change co2"
        assert "Map showing old data" not in result.text
        assert "[[Category:1751 maps of Asia]]" not in result.text
        assert "[[Category:Our World in Data maps of Asia]]" not in result.text
        assert "[[Category:Unrelated maps]]" in result.text
        assert "[[Category:Our World in Data maps of Asia showing 1751 data]]" in result.text
        assert "[[Category:Our World in Data maps showing Absolute change co2]]" in result.text

    @pytest.mark.parametrize(
        ("source_region", "filename_region", "expected_region"),
        [
            ("North America", "North America", "North America"),
            ("North America", "NorthAmerica", "North America"),
            ("South America", "South America", "South America"),
            ("South America", "SouthAmerica", "South America"),
            ("the world", "World", "the world"),
        ],
    )
    def test_normalizes_historical_region_variants(self, source_region, filename_region, expected_region):
        title = f"File:Death rate from opioid use who,{filename_region},2012.svg"
        original = "{{Map showing old data|year=2012}}\n"
        original += f"[[Category:2012 maps of {filename_region}]]\n"
        original += f"[[Category:Our World in Data maps of {filename_region}]]\n"

        result = rewrite_map_page(title, original, source_region)

        assert result.changed is True
        assert result.change is not None
        assert result.change.region == expected_region
        assert f"maps of {expected_region} showing 2012 data" in result.text
        assert "maps showing Death rate from opioid use who" in result.text
        assert f"[[Category:Our World in Data maps of {filename_region}]]" not in result.text

    def test_leaves_file_without_old_data_template_unchanged(self):
        original = "Text\n[[Category:Our World in Data maps of Africa]]\n"

        result = rewrite_map_page("File:Population, Africa, 2020.svg", original, "Africa")

        assert result.changed is False
        assert result.reason == "no old-data template"
        assert result.text == original

    def test_leaves_nonstandard_filename_unchanged_for_manual_review(self):
        original = "{{Map showing old data|year=2020}}\n[[Category:Our World in Data maps of Europe]]\n"

        result = rewrite_map_page("File:Population, Europe.svg", original, "Europe")

        assert result.changed is False
        assert result.reason == "filename does not match the expected map format"
        assert result.text == original

    def test_leaves_conflicting_old_data_years_unchanged(self):
        original = """{{Map showing old data|year=2010}}
{{Map showing old data|year=2011}}
[[Category:Our World in Data maps of Africa]]
"""

        result = rewrite_map_page("File:Population, Africa, 2010.svg", original, "Africa")

        assert result.changed is False
        assert result.reason == "ambiguous old-data years"
        assert result.text == original

    def test_removes_all_duplicate_old_data_templates_with_same_year(self):
        original = """{{Map showing old data|year=2020}}
{{Map showing old data|year=2020}}
[[Category:2020 maps of Oceania]]
[[Category:Our World in Data maps of Oceania]]
"""

        result = rewrite_map_page("File:Population, Oceania, 2020.svg", original, "Oceania")

        assert result.changed is True
        assert result.text.count("Map showing old data") == 0

    def test_does_not_duplicate_destination_categories_already_on_page(self):
        original = """{{Map showing old data|year=2020}}
[[Category:Our World in Data maps of Europe]]
[[Category:Our World in Data maps of Europe showing 2020 data]]
[[Category:Our World in Data maps showing Population]]
"""

        result = rewrite_map_page("File:Population, Europe, 2020.svg", original, "Europe")

        assert result.changed is True
        assert result.text.count("[[Category:Our World in Data maps of Europe showing 2020 data]]") == 1
        assert result.text.count("[[Category:Our World in Data maps showing Population]]") == 1

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("Asia", "Asia"),
            (" NorthAmerica ", "North America"),
            ("southamerica", "South America"),
            ("World", "the world"),
            ("Antarctica", None),
        ],
    )
    def test_normalize_region(self, value, expected):
        assert normalize_region(value) == expected


@pytest.mark.unit
class TestMapRecategorizationOperations:
    """Verify page edits, destination category creation, and batch accounting."""

    @patch("src.main_app.categorize.map_recategorization.commons.MwClientPage")
    @patch("src.main_app.categorize.map_recategorization.commons.ensure_map_category_exists", return_value=True)
    def test_edits_eligible_page_once_after_ensuring_categories(self, ensure_category, page_class):
        page = MagicMock()
        page.get_text.return_value = """{{Map showing old data|year=1948}}
[[Category:1948 maps of Asia]]
[[Category:Our World in Data maps of Asia]]
"""
        page.edit.return_value = {"success": True}
        page_class.return_value = page

        outcome, reason = recategorize_file_page(
            MagicMock(),
            "File:Absolute change co2, Asia, 1948.svg",
            "Asia",
        )

        assert (outcome, reason) == ("recategorized", None)
        assert ensure_category.call_count == 2
        ensured = {call.args[1]: call.args[2] for call in ensure_category.call_args_list}
        assert ensured["Category:Our World in Data maps of Asia showing 1948 data"] == CATEGORY_DESCRIPTION_TEMPLATE
        assert ensured["Category:Our World in Data maps showing Absolute change co2"] == TOPIC_PARENT_CATEGORY
        page.edit.assert_called_once()
        edited_text, summary = page.edit.call_args.args
        assert "Map showing old data" not in edited_text
        assert "Our World in Data maps of Asia]]" not in edited_text
        assert "Recategorize OWID map" in summary

    @patch("src.main_app.categorize.map_recategorization.commons.MwClientPage")
    @patch("src.main_app.categorize.map_recategorization.commons.ensure_map_category_exists", return_value=True)
    def test_dry_run_does_not_edit_page(self, ensure_category, page_class):
        page = MagicMock()
        page.get_text.return_value = (
            "{{Map showing old data|year=2020}}\n[[Category:Our World in Data maps of Europe]]\n"
        )
        page_class.return_value = page

        outcome, reason = recategorize_file_page(
            MagicMock(),
            "File:Population, Europe, 2020.svg",
            "Europe",
            dry_run=True,
        )

        assert (outcome, reason) == ("recategorized", None)
        page.edit.assert_not_called()
        assert all(call.kwargs["dry_run"] is True for call in ensure_category.call_args_list)

    @patch("src.main_app.categorize.map_recategorization.commons.MwClientPage")
    def test_reports_error_when_file_text_is_unavailable(self, page_class):
        page_class.return_value.get_text.return_value = None

        outcome, reason = recategorize_file_page(MagicMock(), "File:Missing.svg", "Africa")

        assert outcome == "error"
        assert reason == "page text could not be retrieved"

    @patch("src.main_app.categorize.map_recategorization.batch.recategorize_file_page")
    @patch("src.main_app.categorize.map_recategorization.batch.get_category_members_titles")
    def test_source_category_batch_counts_each_outcome(self, members, recategorize):
        members.return_value = ["File:One.svg", "File:Two.svg", "File:Three.svg"]
        recategorize.side_effect = [
            ("recategorized", None),
            ("skipped", "no old-data template"),
            ("error", "edit failed"),
        ]

        stats = recategorize_source_category(MagicMock(), "Africa", max_items=3)

        assert stats == {"scanned": 3, "recategorized": 1, "skipped": 1, "errors": 1}
        members.assert_called_once_with(
            recategorize.call_args.args[0],
            "Category:Our World in Data maps of Africa",
            namespace=6,
            max_items=3,
        )

    def test_source_category_rejects_unsupported_region(self):
        with pytest.raises(ValueError, match="Unsupported source region"):
            recategorize_source_category(MagicMock(), "Antarctica")

    def test_category_member_limit_trims_a_large_api_batch(self):
        site = MagicMock()
        site.get.return_value = {
            "query": {
                "categorymembers": [
                    {"title": "File:One.svg"},
                    {"title": "File:Two.svg"},
                    {"title": "File:Three.svg"},
                ]
            },
            "continue": {"cmcontinue": "next-page"},
        }

        titles = get_category_members_titles(
            site,
            "Category:Our World in Data maps of Asia",
            namespace=6,
            max_items=2,
        )

        assert titles == ["File:One.svg", "File:Two.svg"]
        site.get.assert_called_once()
