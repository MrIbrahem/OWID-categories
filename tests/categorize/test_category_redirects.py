"""
Tests for categorize.category_redirects module.
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from categorize.category_redirects import (
    add_category_to_page,
    get_redirect_target,
    resolve_category_redirect,
)


@pytest.mark.unit
class TestAddCategoryToPage:
    """Test adding categories to pages (with mocks)."""

    def test_add_category_to_existing_page(self):
        """Test adding category to an existing page."""
        # Create mock page and site
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Some page text\n[[Category:Existing]]"

        mock_site = Mock()
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        # Test adding category
        category = "Category:Our World in Data graphs of Canada"
        with patch("categorize.wiki.save_page", return_value=True) as mock_save:
            result = add_category_to_page(mock_site, "File:Test.svg", category, dry_run=True)

            assert result is True, "Should return True when category would be added"
            assert mock_page.text.called, "Page text should be checked"
            assert not mock_save.called, "Should not call save_page in dry_run"

    def test_add_category_already_exists(self):
        """Test adding category that already exists."""
        # Create mock page with category already present
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Some page text\n[[Category:Our World in Data graphs of Canada]]"

        mock_site = Mock()
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        # Test adding existing category
        category = "Category:Our World in Data graphs of Canada"
        result = add_category_to_page(mock_site, "File:Test.svg", category, dry_run=True)

        assert result is False, "Should return False when category already exists"

    def test_add_category_page_not_exists(self):
        """Test adding category to non-existent page."""
        # Create mock page that doesn't exist
        mock_page = MagicMock()
        mock_page.exists = False

        mock_site = Mock()
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        # Test adding category
        category = "Category:Our World in Data graphs of Canada"
        result = add_category_to_page(mock_site, "File:NonExistent.svg", category, dry_run=True)

        assert result is False, "Should return False when page doesn't exist"

    def test_add_category_dry_run(self):
        """Test dry-run mode doesn't make actual edits."""
        # Create mock page
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Some page text"

        mock_site = Mock()
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        # Test adding category in dry-run
        category = "Category:Our World in Data graphs of Canada"
        with patch("categorize.wiki.save_page") as mock_save:
            result = add_category_to_page(mock_site, "File:Test.svg", category, dry_run=True)

            assert result is True, "Should return True in dry-run mode"
            assert not mock_save.called, "save_page should not be called in dry-run mode"


@pytest.mark.unit
class TestGetRedirectTarget:
    """Test get_redirect_target function."""

    def test_get_redirect_target_success(self):
        """Test successful retrieval of redirect target."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "{{Category redirect|Category:Target}}"
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = get_redirect_target(mock_site, "Category:Original")
        assert result == "Category:Target"

    def test_get_redirect_target_normalization(self):
        """Test retrieval and normalization of redirect target."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "{{Category redirect|Target without prefix}}"
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = get_redirect_target(mock_site, "Category:Original")
        assert result == "Category:Target without prefix"

    def test_get_redirect_target_no_redirect(self):
        """Test when page has no redirect template."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "[[Category:Parent]]"
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = get_redirect_target(mock_site, "Category:Original")
        assert result is None

    def test_get_redirect_target_page_not_exists(self):
        """Test when page does not exist."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = False
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = get_redirect_target(mock_site, "Category:Nonexistent")
        assert result is None


@pytest.mark.unit
class TestResolveCategoryRedirect:
    """Test category redirect resolution."""

    def test_no_redirect(self):
        """Test category with no redirect template."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "[[Category:Some parent]]"
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        category = "Category:Normal category"
        result = resolve_category_redirect(mock_site, category)
        assert result == category

    def test_standard_redirect(self):
        """Test standard category redirect."""
        mock_site = Mock()

        # Original category page
        mock_page1 = MagicMock()
        mock_page1.exists = True
        mock_page1.text.return_value = "{{Category redirect|Category:Target category}}"

        # Target category page
        mock_page2 = MagicMock()
        mock_page2.exists = True
        mock_page2.text.return_value = "[[Category:Some parent]]"

        pages = {"Category:Original": mock_page1, "Category:Target category": mock_page2}
        mock_site.pages.__getitem__ = Mock(side_effect=lambda x: pages.get(x, MagicMock(exists=False)))

        with patch("time.sleep"):
            result = resolve_category_redirect(mock_site, "Category:Original")
        assert result == "Category:Target category"

    def test_redirect_with_parameter_name(self):
        """Test redirect with 1= parameter."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "{{Category redirect|1=Category:Target category}}"

        mock_target = MagicMock()
        mock_target.exists = True
        mock_target.text.return_value = "text"

        pages = {"Category:Original": mock_page, "Category:Target category": mock_target}
        mock_site.pages.__getitem__ = Mock(side_effect=lambda x: pages.get(x, MagicMock(exists=False)))

        with patch("time.sleep"):
            result = resolve_category_redirect(mock_site, "Category:Original")
        assert result == "Category:Target category"

    def test_redirect_without_category_prefix_in_target(self):
        """Test redirect where target doesn't have Category: prefix."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "{{Category redirect|Target category}}"

        mock_target = MagicMock()
        mock_target.exists = True
        mock_target.text.return_value = "text"

        pages = {"Category:Original": mock_page, "Category:Target category": mock_target}
        mock_site.pages.__getitem__ = Mock(side_effect=lambda x: pages.get(x, MagicMock(exists=False)))

        with patch("time.sleep"):
            result = resolve_category_redirect(mock_site, "Category:Original")
        assert result == "Category:Target category"

    def test_recursive_redirect(self):
        """Test multiple levels of redirects."""
        mock_site = Mock()

        mock_page1 = MagicMock()
        mock_page1.exists = True
        mock_page1.text.return_value = "{{Category redirect|Category:Redirect 2}}"

        mock_page2 = MagicMock()
        mock_page2.exists = True
        mock_page2.text.return_value = "{{Cat redirect|Category:Final target}}"

        mock_page3 = MagicMock()
        mock_page3.exists = True
        mock_page3.text.return_value = "Final content"

        pages = {"Category:Start": mock_page1, "Category:Redirect 2": mock_page2, "Category:Final target": mock_page3}
        mock_site.pages.__getitem__ = Mock(side_effect=lambda x: pages.get(x, MagicMock(exists=False)))

        with patch("time.sleep"):
            result = resolve_category_redirect(mock_site, "Category:Start")
        assert result == "Category:Final target"

    def test_max_depth_reached(self):
        """Test that recursion stops at max_depth."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "{{Category redirect|Category:Infinite}}"
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        # Should return the category after max_depth is reached
        result = resolve_category_redirect(mock_site, "Category:Infinite", max_depth=2)
        assert result == "Category:Infinite"

    def test_complex_wikitext_redirect(self):
        """Test redirect extraction from complex wikitext."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = """
== Summary ==
{{Information
|Description = {{en|A map}}
}}
{{Category redirect|Category:Target}}
[[Category:Some other category]]
"""
        mock_target = MagicMock()
        mock_target.exists = True
        mock_target.text.return_value = "Content"

        pages = {"Category:Original": mock_page, "Category:Target": mock_target}
        mock_site.pages.__getitem__ = Mock(side_effect=lambda x: pages.get(x, MagicMock(exists=False)))

        with patch("time.sleep"):
            result = resolve_category_redirect(mock_site, "Category:Original")
        assert result == "Category:Target"
