#!/usr/bin/env python3
"""
Test script for OWID Commons processing with sample data.

This script demonstrates the functionality without requiring network access.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock

import tempfile
import pytest

from pytest_socket import disable_socket

# tempfile.gettempdir() returns the path to the system's directory for temporary files
system_temp_dir = Path(tempfile.gettempdir())

# Now correctly combine it with "test" and set the environment variable
os.environ["SUMMARY_FILE_BACKUP"] = str(system_temp_dir / "summary_file_backup.json")
os.environ["MAIN_DIR"] = str(system_temp_dir / "test")

@pytest.fixture(autouse=True)
def stop_nets(request):
    # Check if 'network' mark is present in the current test item
    if "network" in request.node.keywords:
        from pytest_socket import enable_socket

        enable_socket()
        return
    # Otherwise, disable the socket for all other tests
    disable_socket(allow_unix_socket=True)


@pytest.fixture#(autouse=True)
def mock_dump_to_file(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    # src/main_app/files_dumper.py
    monkeypatch.setattr("src.main_app.files_dumper.dump_to_file", lambda *args, **kwargs: None)
    return MagicMock()

# ── mwclient_page fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_site() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_page() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_site_pages(mock_site, mock_page):
    def _factory(page_exists: bool) -> MagicMock:
        mock_page.exists = page_exists

        mock_pages = MagicMock()
        mock_pages.__getitem__ = MagicMock(return_value=mock_page)

        mock_site.pages = mock_pages
        return mock_site

    return _factory
