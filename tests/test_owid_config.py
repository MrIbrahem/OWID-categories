#!/usr/bin/env python3
"""
"""


from src.main_app.owid_config import main_dir


def test_main_dir() -> None:
    assert main_dir != "/Users/owid/owid-data"
