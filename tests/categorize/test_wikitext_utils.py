"""
Tests for categorize.wikitext_utils module.
"""

import pytest

from categorize.wikitext_utils import (
    category_exists_on_page,
    extract_redirect_target,
)


@pytest.mark.unit
class TestCategoryExistsOnPage:
    """Test category existence checking."""

    def test_category_found_standard_format(self):
        """Test category is found with standard format."""
        page_text = """
Some file description here.
{{Information
|Description={{en|1=Agriculture share of GDP}}
}}

[[Category:Our World in Data graphs of Canada]]
[[Category:Economic indicators]]
"""
        result = category_exists_on_page(page_text, "Category:Our World in Data graphs of Canada")
        assert result is True, "Category should be found when present"

    def test_category_not_found(self):
        """Test category is not found when absent."""
        page_text = """
Some file description here.
{{Information
|Description={{en|1=Agriculture share of GDP}}
}}

[[Category:Economic indicators]]
"""
        result = category_exists_on_page(page_text, "Category:Our World in Data graphs of Canada")
        assert result is False, "Category should not be found when absent"

    def test_category_found_lowercase(self):
        """Test category check is case-insensitive."""
        page_text = "[[category:Our World in Data graphs of Canada]]"
        result = category_exists_on_page(page_text, "Category:Our World in Data graphs of Canada")
        assert result is True, "Category check should be case-insensitive"

    def test_empty_page_text(self):
        """Test with empty page text."""
        result = category_exists_on_page("", "Category:Our World in Data graphs of Canada")
        assert result is False, "Should return False for empty page text"

    def test_none_page_text(self):
        """Test with None page text."""
        result = category_exists_on_page(None, "Category:Our World in Data graphs of Canada")  # type: ignore
        assert result is False, "Should return False for None page text"


@pytest.mark.unit
class TestExtractRedirectTarget:
    """Test extraction of redirect target from wikitext."""

    def test_extract_standard_redirect(self):
        """Test extraction from {{Category redirect|Target}}."""
        wikitext = "{{Category redirect|Category:Target category}}"
        assert extract_redirect_target(wikitext) == "Category:Target category"

    def test_extract_alias_redirect(self):
        """Test extraction from {{Cat redirect|Target}}."""
        wikitext = "{{Cat redirect|Category:Target category}}"
        assert extract_redirect_target(wikitext) == "Category:Target category"

    def test_extract_named_parameter(self):
        """Test extraction from {{Category redirect|1=Target}}."""
        wikitext = "{{Category redirect|1=Category:Target category}}"
        assert extract_redirect_target(wikitext) == "Category:Target category"

    def test_extract_missing_parameter(self):
        """Test extraction when parameter is missing."""
        wikitext = "{{Category redirect}}"
        assert extract_redirect_target(wikitext) is None

    def test_extract_no_redirect(self):
        """Test extraction when no redirect template is present."""
        wikitext = "[[Category:Some category]]"
        assert extract_redirect_target(wikitext) is None

    def test_extract_multiple_templates(self):
        """Test extraction when multiple templates are present."""
        wikitext = """
{{Information|Description=Test}}
{{Category redirect|Category:Target}}
[[Category:Parent]]
"""
        assert extract_redirect_target(wikitext) == "Category:Target"
