#!/usr/bin/env python3
"""
Test script for OWID Commons processing with sample data.

This script demonstrates the functionality without requiring network access.
"""

import sys
from pathlib import Path

import pytest
from pytest_socket import disable_socket

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def stop_nets(request):
    # Check if 'network' mark is present in the current test item
    if "network" in request.node.keywords:
        from pytest_socket import enable_socket

        enable_socket()
        return
    # Otherwise, disable the socket for all other tests
    disable_socket(allow_unix_socket=True)
