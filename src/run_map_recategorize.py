#!/usr/bin/env python3
"""Recategorize OWID continent and world maps on Wikimedia Commons.

The command is intentionally rerunnable: it processes only files that remain
in the old broad category, and it changes a page only when it contains the
``Map showing old data`` template.
"""

from __future__ import annotations

import argparse
import logging

from main_app.categorize import connect_to_commons
from main_app.categorize.map_recategorization import REGION_ALIASES, recategorize_source_category
from main_app.logger_config import setup_logging
from main_app.owid_config import LOG_FILE_CONTINENTS, load_credentials

logger = logging.getLogger(__name__)


def _parse_regions(value: str) -> list[str]:
    requested = [region.strip() for region in value.split(",") if region.strip()]
    unknown = [region for region in requested if region not in REGION_ALIASES]
    if unknown:
        valid = ", ".join(REGION_ALIASES)
        raise argparse.ArgumentTypeError(f"Unsupported region(s): {', '.join(unknown)}. Choose from: {valid}")
    return requested


def main() -> None:
    parser = argparse.ArgumentParser(description="Recategorize legacy OWID continent and world maps")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without creating or editing pages")
    parser.add_argument(
        "--regions",
        type=_parse_regions,
        default=list(REGION_ALIASES),
        help="Comma-separated source regions; defaults to every supported region",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        help="Maximum files to scan from each source category; use for a small pilot batch",
    )
    args = parser.parse_args()

    if args.max_items is not None and args.max_items <= 0:
        parser.error("--max-items must be a positive integer")

    setup_logging(
        level="INFO",
        name="main_app",
        log_file=str(LOG_FILE_CONTINENTS),
        use_colorlog=False,
        overwrite=True,
        use_console=True,
    )

    username, password = load_credentials()
    if not username or not password:
        logger.error("Missing Wikimedia Commons bot credentials in .env")
        return

    site = connect_to_commons(username, password)
    if not site:
        logger.error("Failed to connect to Wikimedia Commons")
        return

    totals = {"scanned": 0, "recategorized": 0, "skipped": 0, "errors": 0}
    for region in args.regions:
        logger.info("Processing source category for %s", region)
        stats = recategorize_source_category(
            site,
            region,
            dry_run=args.dry_run,
            max_items=args.max_items,
        )
        for key, value in stats.items():
            totals[key] += value
        logger.info("%s: %s", region, stats)

    logger.info("Final summary: %s", totals)
    if args.dry_run:
        logger.info("Dry run complete; no Commons pages were edited.")


if __name__ == "__main__":
    main()
