"""
Reads the "Messaged to update application" section of
https://meta.wikimedia.org/wiki/Hardware_donation_program
and, for each linked subpage, prints:
  - last edit timestamp of that subpage
  - the global edit count of the user who created it
"""

import logging
from pathlib import Path
from typing import Optional

import mwclient
import mwclient.errors
import wikitextparser as wtp
from mwclient.client import Site

from ..owid_config import USER_AGENT, load_credentials

API_URL = "https://meta.wikimedia.org/w/api.php"
BASE_PAGE = "Hardware donation program"
SECTION_HEADING = "Messaged to update application"
OUTPUT_FILE = Path(__file__).parent / "file.wiki"
OUTPUT_FILE_TABLE = Path(__file__).parent / "table.wiki"

logger = logging.getLogger(__name__)


def connect_to_meta(username: str, password: str) -> Optional[Site]:
    """
    Connect to Wikimedia Commons using mwclient.

    Args:
        username: Bot username
        password: Bot password

    Returns:
        Connected Site object or None on failure
    """
    try:
        logger.info("Connecting to meta.wikimedia.org...")
        site = Site("meta.wikimedia.org", clients_useragent=USER_AGENT)

        logger.info(f"Logging in as {username}...")
        site.login(username, password)

        logger.info("Successfully connected and logged in")
        return site
    except mwclient.errors.LoginError as e:
        logger.error(f"Login failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"Failed to connect to meta.wikimedia.org: {e}")
        return None


def get_page_wikitext(site, page_title):
    """Fetch the full raw wikitext of a page via the API."""
    params = {
        "prop": "revisions",
        "titles": page_title,
        "rvslots": "main",
        "rvprop": "content",
        "formatversion": 2,
        "format": "json",
    }
    try:
        data = site.get("query", **params)
    except Exception as e:
        logger.error("API request failed %s", str(e))

    pages = data.get("query", {}).get("pages", [])

    return pages[0]["revisions"][0]["slots"]["main"]["content"]


def get_section_by_heading(wikitext, heading):
    """Use wikitextparser to find a section by its heading text."""
    parsed = wtp.parse(wikitext)
    for section in parsed.get_sections(include_subsections=False):
        if section.title and section.title.strip() == heading:
            return section
    raise ValueError(f"Section '{heading}' not found")


def extract_subpage_links(section, base_page):
    """Use wikitextparser's wikilinks to pull out 'Base/Sub' page names."""
    prefix = base_page + "/"
    seen = []
    for link in section.wikilinks:
        title = link.title.strip()
        if title.startswith(prefix):
            name = title[len(prefix) :]
            if name not in seen:
                seen.append(name)
    return seen


def get_last_edit_timestamp(site, page_title):
    params = {
        "prop": "revisions",
        "titles": page_title,
        "rvlimit": 1,
        "rvprop": "timestamp",
        "formatversion": 2,
        "format": "json",
    }
    try:
        data = site.get("query", **params)
    except Exception as e:
        logger.error("API request failed %s", str(e))
        return None

    pages = data.get("query", {}).get("pages", [])
    if pages and "revisions" in pages[0]:
        return pages[0]["revisions"][0]["timestamp"]

    return None


def get_page_creator(site, page_title):
    """Username of the oldest revision (i.e. who created the page)."""
    params = {
        "prop": "revisions",
        "titles": page_title,
        "rvlimit": 1,
        "rvdir": "newer",
        "rvprop": "user",
        "formatversion": 2,
        "format": "json",
    }

    try:
        data = site.get("query", **params)
    except Exception as e:
        logger.error("API request failed %s", str(e))
        return None

    pages = data.get("query", {}).get("pages", [])
    if pages and "revisions" in pages[0]:
        return pages[0]["revisions"][0]["user"]

    return None


def get_global_editcount(site, username):
    params = {
        "list": "globalusers",
        "gusprop": "editcount",
        "gususers": username,
        "formatversion": 2,
        "format": "json",
    }

    try:
        data = site.get("query", **params)
    except Exception as e:
        logger.error("API request failed %s", str(e))
        return None

    users = data.get("query", {}).get("globalusers", [])
    if users:
        return users[0].get("editcount")
    return None


def build_wikitable(rows):
    """rows: list of (page_link, last_edit, user_link, editcount_str) tuples."""
    lines = ['{| class="wikitable sortable"', "! Page !! Last edited !! User !! Global edits"]
    for page_link, last_edit, user_link, editcount_str in rows:
        lines.append("|-")
        lines.append(f"| {page_link} || {last_edit} || {user_link} || {editcount_str}")
    lines.append("|}")
    return "\n".join(lines)


def main() -> None:
    # Load credentials

    # Load credentials
    username, password = load_credentials()
    if not username or not password:
        logger.error("Failed to load credentials from .env file")
        logger.error("Please create a .env file with WIKIPEDIA_BOT_USERNAME and WIKIPEDIA_BOT_PASSWORD")
        return

    # Connect to Commons
    site = connect_to_meta(username, password)
    if not site:
        logger.error("Failed to connect to Wikimedia Commons")
        return

    full_wikitext = get_page_wikitext(site, BASE_PAGE)
    section = get_section_by_heading(full_wikitext, SECTION_HEADING)
    subpages = extract_subpage_links(section, BASE_PAGE)

    lines = [f"=== {SECTION_HEADING} ===", ""]
    rows = []
    for sub in subpages:
        full_title = f"{BASE_PAGE}/{sub}"
        last_edit = get_last_edit_timestamp(site, full_title) or "unknown"
        username = get_page_creator(site, full_title)
        editcount = get_global_editcount(site, username) if username else None
        editcount_str = f"{editcount:,}" if isinstance(editcount, int) else "unknown"
        line = f"*[[{full_title}]] (Last edited: {last_edit}, {username or 'unknown'} global edits: {editcount_str})"
        lines.append(line)

        page_link = f"[[{full_title}]]"
        user_link = f"[[User:{username}]]" if username else "unknown"

        rows.append((page_link, last_edit, user_link, editcount_str))

    table = build_wikitable(rows)
    output_table = f"=== {SECTION_HEADING} ===\n\n{table}\n"
    OUTPUT_FILE_TABLE.write_text(output_table, encoding="utf-8")

    output_text = "\n".join(lines) + "\n"
    OUTPUT_FILE.write_text(output_text, encoding="utf-8")
    print(output_text)
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
