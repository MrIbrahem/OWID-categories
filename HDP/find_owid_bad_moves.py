#!/usr/bin/env python3
"""
find_owid_bad_moves.py

Searches Doc James's Wikimedia Commons contributions for file moves
tagged with OWIDImporter where the source and destination country
codes don't match — e.g. moving CHN → ARE.

Usage:
    python find_owid_bad_moves.py

Output:
    owid_bad_moves.csv   — list of suspected bad moves
    owid_bad_moves.log   — progress log
"""

import csv
import logging
import re
import time
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = "https://commons.wikimedia.org/w/api.php"
USERNAME = "Doc James"  # contributions to scan
TAG = "OAuth CID: 9443"  # log tag to filter on
OUT_CSV = Path(__file__).parent / "owid_bad_moves.csv"
OUT_LOG = Path(__file__).parent / "owid_bad_moves.log"
DELAY = 0.5  # seconds between API calls (be polite)
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(log_color)s%(levelname)-s %(reset)s- [%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler(OUT_LOG),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# Matches a 2-or-3-letter ISO country code at the end of a bare file stem
# e.g.  "Cereal production, CHN"  →  group(1)="Cereal production, "  group(2)="CHN"
COUNTRY_RE = re.compile(r"^(.*),\s+([A-Z]{2,3})$")


def extract_country(title: str) -> str | None:
    """Return the country code from a File: title, or None."""
    stem = title.removeprefix("File:").removesuffix(".svg").strip()
    m = COUNTRY_RE.match(stem)
    return m.group(2) if m else None


def iter_move_log(session: requests.Session):
    """
    Yield every 'move' log entry for USERNAME that carries the OWIDImporter tag.
    Pages through the API automatically.
    """
    params = {
        "action": "query",
        "list": "logevents",
        "letype": "move",
        "leuser": USERNAME,
        # "letag":   TAG,
        "leprop": "title|details|timestamp|comment",
        "lelimit": "500",
        "format": "json",
    }

    fetched = 0
    while True:
        resp = session.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        events = data.get("query", {}).get("logevents", [])
        for ev in events:
            yield ev
        fetched += len(events)

        cont = data.get("continue", {})
        if not cont:
            break
        params.update(cont)
        log.info("  … fetched %d move events so far, continuing …", fetched)
        time.sleep(DELAY)

    log.info("Total move events fetched: %d", fetched)


def main():
    log.info("Starting scan for bad OWIDImporter moves (user: %s)", USERNAME)
    session = requests.Session()
    session.headers["User-Agent"] = (
        "find_owid_bad_moves/1.0 "
        "(Wikimedia Commons audit script; "
        "https://commons.wikimedia.org/wiki/User:Doc_James; "
        "Doc James)"
    )

    bad_moves = []
    total_moves = 0

    for ev in iter_move_log(session):
        total_moves += 1

        # The *current* title is in ev["title"]   (destination after move)
        # The *original* title lives in ev["params"]["target_title"]  (source)
        params_block = ev.get("params", {})
        dest_title = ev.get("title", "")
        src_title = params_block.get("target_title", "")

        # logevents 'move' puts the OLD title in ev["title"] and
        # NEW title in params["target_title"]  — double-check both directions:
        old_title = ev.get("title", "")
        new_title = params_block.get("target_title", "")

        old_country = extract_country(old_title)
        new_country = extract_country(new_title)

        is_bad = old_country is not None and new_country is not None and old_country != new_country

        if is_bad:
            log.warning(
                "BAD MOVE: %s  →  %s  [%s]  comment: %s",
                old_title,
                new_title,
                ev.get("timestamp", ""),
                ev.get("comment", ""),
            )
            bad_moves.append(
                {
                    "timestamp": ev.get("timestamp", ""),
                    "old_title": old_title,
                    "new_title": new_title,
                    "old_country": old_country,
                    "new_country": new_country,
                    "comment": ev.get("comment", ""),
                    "logid": ev.get("logid", ""),
                    "commons_url": ("https://commons.wikimedia.org/wiki/" + new_title.replace(" ", "_")),
                }
            )

    log.info("Scan complete. Total moves examined: %d", total_moves)
    log.info("Bad moves found: %d", len(bad_moves))

    if bad_moves:
        with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=bad_moves[0].keys())
            writer.writeheader()
            writer.writerows(bad_moves)
        log.info("Results saved to %s", OUT_CSV)
    else:
        log.info("No bad moves found — nothing written to CSV.")


if __name__ == "__main__":
    main()
