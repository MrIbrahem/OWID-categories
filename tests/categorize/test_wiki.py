"""
Tests for categorize.wiki module.

Tests Wiki API functions for authentication, page editing,
and category management on Wikimedia Commons.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock, patch

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from categorize.wiki import (
    category_exists_on_page,
    add_category_to_page,
    ensure_category_exists,
    get_category_member_count,
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
        result = category_exists_on_page(
            page_text,
            "Category:Our World in Data graphs of Canada"
        )
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
        result = category_exists_on_page(
            page_text,
            "Category:Our World in Data graphs of Canada"
        )
        assert result is False, "Category should not be found when absent"

    def test_category_found_lowercase(self):
        """Test category check is case-insensitive."""
        page_text = "[[category:Our World in Data graphs of Canada]]"
        result = category_exists_on_page(
            page_text,
            "Category:Our World in Data graphs of Canada"
        )
        assert result is True, "Category check should be case-insensitive"

    def test_empty_page_text(self):
        """Test with empty page text."""
        result = category_exists_on_page(
            "",
            "Category:Our World in Data graphs of Canada"
        )
        assert result is False, "Should return False for empty page text"

    def test_none_page_text(self):
        """Test with None page text."""
        result = category_exists_on_page(
            None,
            "Category:Our World in Data graphs of Canada"
        )
        assert result is False, "Should return False for None page text"


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
        result = add_category_to_page(
            mock_site,
            "File:Test.svg",
            category,
            dry_run=True
        )

        assert result is True, "Should return True when category would be added"
        assert mock_page.text.called, "Page text should be checked"

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
        result = add_category_to_page(
            mock_site,
            "File:Test.svg",
            category,
            dry_run=True
        )

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
        result = add_category_to_page(
            mock_site,
            "File:NonExistent.svg",
            category,
            dry_run=True
        )

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
        result = add_category_to_page(
            mock_site,
            "File:Test.svg",
            category,
            dry_run=True
        )

        assert result is True, "Should return True in dry-run mode"
        assert not mock_page.save.called, "Page should not be saved in dry-run mode"


@pytest.mark.unit
class TestEnsureCategoryExists:
    """Test ensuring category pages exist."""

    def test_category_already_exists(self):
        """Test when category already exists."""
        mock_site = Mock()
        mock_page_exists = MagicMock()
        mock_page_exists.exists = True
        mock_site.pages.__getitem__ = Mock(return_value=mock_page_exists)

        result = ensure_category_exists(
            mock_site,
            "Category:Our World in Data graphs of Canada",
            "Our World in Data graphs by country",
            "Canada",
            dry_run=True
        )
        assert result is True, "Should return True when category already exists"

    def test_category_not_exists_dry_run(self):
        """Test creating category in dry-run mode."""
        mock_site = Mock()
        mock_page_not_exists = MagicMock()
        mock_page_not_exists.exists = False
        mock_site.pages.__getitem__ = Mock(return_value=mock_page_not_exists)

        result = ensure_category_exists(
            mock_site,
            "Category:Our World in Data graphs of Brazil",
            "Our World in Data graphs by country",
            "Brazil",
            dry_run=True
        )
        assert result is True, "Should return True in dry-run mode"
        assert not mock_page_not_exists.save.called, "Should not save in dry-run mode"

    def test_category_with_the_prefix(self):
        """Test creating category for country with 'the' prefix."""
        mock_site = Mock()
        mock_page_not_exists = MagicMock()
        mock_page_not_exists.exists = False
        mock_site.pages.__getitem__ = Mock(return_value=mock_page_not_exists)

        result = ensure_category_exists(
            mock_site,
            "Category:Our World in Data graphs of the United Kingdom",
            "Our World in Data graphs by country",
            "United Kingdom",
            dry_run=True
        )
        assert result is True, "Should return True for countries with 'the' prefix in dry-run mode"


@pytest.mark.unit
class TestGetCategoryMemberCount:
    """Test counting category members."""

    def test_count_members_existing_category(self):
        """Test counting members in an existing category."""
        # Create mock category page with members
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.members.return_value = [
            Mock(),
            Mock(),
            Mock(),
        ]  # 3 members

        mock_site = Mock()
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = get_category_member_count(
            mock_site,
            "Category:Our World in Data graphs of Canada"
        )
        assert result == 3, "Should return correct member count"

    def test_count_members_nonexistent_category(self):
        """Test counting members in a non-existent category."""
        # Create mock page that doesn't exist
        mock_page = MagicMock()
        mock_page.exists = False

        mock_site = Mock()
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = get_category_member_count(
            mock_site,
            "Category:Nonexistent Category"
        )
        assert result == 0, "Should return 0 for non-existent category"

    def test_count_members_empty_category(self):
        """Test counting members in an empty category."""
        # Create mock category page with no members
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.members.return_value = []

        mock_site = Mock()
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = get_category_member_count(
            mock_site,
            "Category:Our World in Data graphs of Empty Country"
        )
        assert result == 0, "Should return 0 for empty category"


@pytest.mark.api
class TestMockCategorization:
    """Test the categorization workflow with mock objects."""

    def test_mock_page_setup(self):
        """Test basic mock page setup."""
        # Create a mock page
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Some page text\n[[Category:Existing]]"

        # Assertions
        assert mock_page.exists is True, "Mock page should exist"
        assert "Category:Existing" in mock_page.text(), "Mock page should contain existing category"

    def test_simulate_adding_category(self):
        """Simulate adding a category to page text."""
        # Create mock page
        mock_page = MagicMock()
        mock_page.text.return_value = "Some page text\n[[Category:Existing]]"

        # Simulate adding a category
        category = "Category:Our World in Data graphs of Canada"
        current_text = mock_page.text()
        new_text = current_text.rstrip() + f"\n[[{category}]]\n"

        # Assertions
        assert category in new_text, "New category should be in the updated text"
        assert len(new_text) > len(current_text), "New text should be longer than current text"
        assert new_text.endswith(f"[[{category}]]\n"), "Category should be added at the end"
