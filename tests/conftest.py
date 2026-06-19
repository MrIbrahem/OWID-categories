#!/usr/bin/env python3
"""
Test script for OWID Commons processing with sample data.

This script demonstrates the functionality without requiring network access.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
