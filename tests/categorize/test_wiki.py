"""
Tests for categorize.wiki module.

Tests Wiki API functions for authentication, page editing,
and category management on Wikimedia Commons.
"""

from unittest.mock import MagicMock, Mock

import pytest

from src.main_app.categorize.wiki import (
    ensure_category_exists,
)


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
