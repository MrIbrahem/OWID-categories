#!/usr/bin/env python3
"""
OWID Commons Continents Categorizer

This script automatically adds continent-specific categories to OWID graph files on Wikimedia Commons.
It reads JSON files and adds categories in the format:
    Category:Our World in Data graphs of {Continent}

Requirements:
- Python 3.10+
- mwclient library
- python-dotenv library
- Valid Wikimedia Commons bot credentials in .env file

Usage:
    python run_continents.py                             # Process all continents
    python run_continents.py --dry-run                   # Test without making edits
    python run_continents.py --limit 2                   # Process first 2 continents only
    python run_continents.py --files-per-continent 10    # Process 10 files per continent
"""

import argparse
import mwclient
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Optional

from categorize.wiki import (
    connect_to_commons,
    load_credentials,
    add_category_to_page,
    ensure_category_exists,
    get_category_member_count,
    get_edit_delay,
)
from categorize.utils import (
    setup_logging,
    load_json_file,
    build_category_name,
    get_parent_category,
)


# Configuration
CONTINENTS_DIR = Path("output/continents")
LOG_FILE = Path("logs/categorize_continents.log")


# List of continents to process
CONTINENTS = [
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "Oceania",
]


def process_continent_file(
    site: mwclient.Site,
    file_path: Path,
    dry_run: bool = False,
    graphs_only: bool = True,
    files_per_continent: Optional[int] = None
) -> Dict[str, int]:
    """
    Process a single continent JSON file and add categories to its files.

    Args:
        site: Connected mwclient Site
        file_path: Path to continent JSON file
        dry_run: If True, don't actually make edits
        graphs_only: If True, only process graph files (not maps)
        files_per_continent: Optional limit on number of files to process per continent

    Returns:
        Dictionary with statistics (added, skipped, errors)
    """
    stats = {
        "added": 0,
        "skipped": 0,
        "errors": 0
    }

    # Load continent data
    data = load_json_file(file_path)
    if not data:
        stats["errors"] += 1
        return stats

    continent = data.get("continent")
    graphs = data.get("graphs", [])

    if not continent:
        logging.error(f"No continent name in {file_path}")
        stats["errors"] += 1
        return stats

    # Build category name
    category = build_category_name(continent, "continent", "graphs")

    # Check if category already has enough files when files_per_continent is set
    if files_per_continent:
        current_member_count = get_category_member_count(site, category)
        if current_member_count >= files_per_continent:
            logging.info(f"\nSkipping {continent}: Category already has {current_member_count} files (>= {files_per_continent} requested)")
            return stats
        logging.info(f"\nProcessing {continent}: Category has {current_member_count} files, will add up to {files_per_continent} files")
    else:
        logging.info(f"\nProcessing {continent}: {len(graphs)} graphs")

    # Apply per-continent file limit if specified
    if files_per_continent:
        graphs = graphs[:files_per_continent]
        logging.info(f"Limiting to {files_per_continent} file(s) per continent")

    # Ensure the category page exists before adding files to it
    parent_category = get_parent_category("continent")
    if not ensure_category_exists(site, category, parent_category, continent, dry_run):
        logging.error(f"Failed to ensure category '{category}' exists for {continent}, skipping this continent")
        stats["errors"] += 1
        return stats

    # Process graphs
    for graph in graphs:
        title = graph.get("title")
        if not title:
            logging.warning(f"Graph missing title in {file_path}")
            stats["errors"] += 1
            continue

        # Add category
        if add_category_to_page(site, title, category, dry_run):
            stats["added"] += 1
        else:
            stats["skipped"] += 1

        # Rate limiting
        if not dry_run:
            time.sleep(get_edit_delay())

    return stats


def main(dry_run: bool = False, limit: Optional[int] = None, files_per_continent: Optional[int] = None):
    """
    Main execution function for continents categorization.

    Args:
        dry_run: If True, don't actually make edits
        limit: Optional limit on number of continents to process
        files_per_continent: Optional limit on number of files to process per continent
    """
    setup_logging(LOG_FILE)

    logging.info("=" * 80)
    logging.info("OWID Commons Continents Categorizer")
    logging.info("=" * 80)

    if dry_run:
        logging.info("Running in DRY RUN mode - no actual edits will be made")

    if files_per_continent:
        logging.info(f"Processing {files_per_continent} file(s) per continent")

    # Load credentials
    username, password = load_credentials()
    if not username or not password:
        logging.error("Failed to load credentials from .env file")
        logging.error("Please create a .env file with WM_USERNAME and PASSWORD")
        sys.exit(1)

    # Connect to Commons
    site = connect_to_commons(username, password)
    if not site:
        logging.error("Failed to connect to Wikimedia Commons")
        sys.exit(1)

    # Check if continents directory exists
    if not CONTINENTS_DIR.exists():
        logging.error(f"Continents directory not found: {CONTINENTS_DIR}")
        logging.error("Please ensure continent JSON files are available")
        sys.exit(1)

    # Get all continent JSON files
    continent_files = sorted(CONTINENTS_DIR.glob("*.json"))

    if not continent_files:
        logging.error(f"No continent JSON files found in {CONTINENTS_DIR}")
        sys.exit(1)

    logging.info(f"Found {len(continent_files)} continent files")

    # Apply limit if specified
    if limit:
        continent_files = continent_files[:limit]
        logging.info(f"Processing limited to first {limit} continents")    # Process each continent file
    total_stats = {
        "added": 0,
        "skipped": 0,
        "errors": 0,
        "continents_processed": 0,
        "continents_skipped": 0
    }

    for file_path in continent_files:
        stats = process_continent_file(site, file_path, dry_run=dry_run, files_per_continent=files_per_continent)

        # If no files were added or skipped, the continent was skipped entirely
        if stats["added"] == 0 and stats["skipped"] == 0 and stats["errors"] == 0:
            total_stats["continents_skipped"] += 1
        else:
            total_stats["added"] += stats["added"]
            total_stats["skipped"] += stats["skipped"]
            total_stats["errors"] += stats["errors"]
            total_stats["continents_processed"] += 1

    # Final summary
    logging.info("\n" + "=" * 80)
    logging.info("FINAL SUMMARY")
    logging.info("=" * 80)
    logging.info(f"Continents processed: {total_stats['continents_processed']}")
    logging.info(f"Continents skipped (already have enough files): {total_stats['continents_skipped']}")
    logging.info(f"Categories added: {total_stats['added']}")
    logging.info(f"Already had category (skipped): {total_stats['skipped']}")
    logging.info(f"Errors: {total_stats['errors']}")
    logging.info("=" * 80)

    if dry_run:
        logging.info("\nThis was a DRY RUN - no actual edits were made")
        logging.info("Run without --dry-run flag to make actual edits")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add continent categories to OWID graph files on Wikimedia Commons"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual edits)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit processing to first N continents (for testing)"
    )
    parser.add_argument(
        "--files-per-continent",
        type=int,
        help="Limit processing to N files per continent (for testing)"
    )

    args = parser.parse_args()

    main(dry_run=args.dry_run, limit=args.limit, files_per_continent=args.files_per_continent)
