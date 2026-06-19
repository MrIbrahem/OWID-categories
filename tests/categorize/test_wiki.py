"""
Tests for categorize.wiki module.

Tests Wiki API functions for authentication, page editing,
and category management on Wikimedia Commons.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.categorize.wiki import (
    ensure_category_exists,
    get_page_text,
    save_page,
)


@pytest.mark.unit
class TestSavePage:
    """Test saving pages."""

    def test_save_page_success(self):
        """Test successful page save."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        with patch("time.sleep"):
            result = save_page(mock_site, "Title", "Text", "Summary")

        assert result is True
        mock_page.edit.assert_called_once_with("Text", summary="Summary")

    def test_save_page_failure(self):
        """Test page save failure."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.edit.side_effect = Exception("Save failed")
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = save_page(mock_site, "Title", "Text", "Summary")
        assert result is False


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
            dry_run=True,
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
            dry_run=True,
        )
        assert result is True, "Should return True in dry-run mode"
        assert not mock_page_not_exists.edit.called, "Should not save in dry-run mode"

    def test_category_creation_success(self):
        """Test successful category creation."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = False
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        with patch("categorize.wiki.save_page", return_value=True) as mock_save:
            result = ensure_category_exists(mock_site, "Category:Test", "Parent", "Sort")
            assert result is True
            mock_save.assert_called_once()


@pytest.mark.unit
class TestGetPageText:
    """Test get_page_text with retries."""

    def test_get_page_text_success(self):
        """Test successful page text retrieval."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Content"
        mock_site.pages.__getitem__ = Mock(return_value=mock_page)

        result = get_page_text(mock_site, "Title")
        assert result == "Content"

    def test_get_page_text_retry_success(self):
        """Test successful page text retrieval after a failure."""
        mock_site = Mock()
        mock_page = MagicMock()
        mock_page.exists = True
        mock_page.text.return_value = "Content"

        # First call fails, second succeeds
        mock_site.pages.__getitem__ = Mock(side_effect=[Exception("Transient error"), mock_page])

        with patch("time.sleep"):  # Skip delay in tests
            result = get_page_text(mock_site, "Title")
        assert result == "Content"
        assert mock_site.pages.__getitem__.call_count == 2

    def test_get_page_text_permanent_failure(self):
        """Test permanent failure after max retries."""
        mock_site = Mock()
        mock_site.pages.__getitem__ = Mock(side_effect=Exception("Permanent error"))

        with patch("time.sleep"):
            result = get_page_text(mock_site, "Title", max_retries=2)
        assert result is None
        assert mock_site.pages.__getitem__.call_count == 2
