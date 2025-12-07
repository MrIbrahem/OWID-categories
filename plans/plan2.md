# Phase 2 — Automated Categorization of OWID Graph Files on Wikimedia Commons

## 0. Overview

This stage builds on the output JSON files generated in **Phase 1** (`output/countries/*.json`)
and programmatically adds the correct **country graph categories** to corresponding files on Wikimedia Commons.

Each country's graph files will be categorized as follows:

- Example:
  - `"CAN"` → `Category:Our World in Data graphs of Canada`
  - `"BRA"` → `Category:Our World in Data graphs of Brazil`
  - `"EGY"` → `Category:Our World in Data graphs of Egypt`

All updates are performed using the **MediaWiki API via `mwclient`**, with credentials securely loaded from a `.env` file.

---

## 1. Requirements and Setup

### 1.1 Libraries

- `mwclient`
- `json`
- `os`
- `dotenv` (`python-dotenv`)
- `logging`
- `pathlib`

Install dependencies:

```bash
pip install mwclient python-dotenv
```

---

## 2. Environment Configuration

Create a `.env` file:

```bash
WM_USERNAME=YourBotUsername
PASSWORD=YourSecurePassword
```

Do not commit this file to version control.

---

## 3. Authentication via `mwclient`

### 3.1 Load credentials

```python
from dotenv import load_dotenv
import os

load_dotenv()
WM_USERNAME = os.getenv("WM_USERNAME")
PASSWORD = os.getenv("PASSWORD")
```

### 3.2 Connect

```python
import mwclient

site = mwclient.Site("commons.wikimedia.org")
site.login(WM_USERNAME, PASSWORD)
```

---

## 4. Input Source

Use JSON files from `output/countries/*.json` generated in Phase 1.

---

## 5. Category Construction

```
Category:Our World in Data graphs of {Country}
```

Example:

```
Category:Our World in Data graphs of Canada
```

---

## 6. Editing Workflow

1. Iterate through JSON files.
2. For each country:
   - Build category title: `Category:Our World in Data graphs of {Country}`
   - Check if category page exists using `site.pages[category_title].exists`
   - If category page does not exist:
     - Create page with content: `[[Category:Our World in Data graphs by country|{Country}]]`
     - Save with edit summary: `"Create category for {Country} OWID graphs (automated)"`
3. For each graph:
   - Load Commons page.
   - Check if category already exists on the file page.
   - If not, append category.
   - Save edit with summary:
     `"Add Our World in Data graphs of {Country} (automated)"`

Include a **dry-run mode** before performing real edits.

---

## 7. Safety

- Respect Wikimedia rate limits.
- Delay between edits (1–2 seconds).
- Log successes, skips, and errors.
- Provide final summary.

---

## 8. User-Agent Requirement

Always include a descriptive User-Agent in every request:

```
OWID-Commons-Categorizer/1.0 (contact: your-email@example.com)
```

---

## 9. Final Checklist

- Test on a few files first.
- Validate edits manually.
- Run full script.
- Review logs carefully.
