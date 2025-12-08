# OWID Commons Processing Plan

## 0. Overview

Goal: Build a Python script that:

1. Fetches **all files** in `Category:Uploaded_by_OWID_importer_tool` from Wikimedia Commons.
2. Classifies each file as either:
   - **Graph** (time series for a country, e.g. `Agriculture share gdp, 1997 to 2021, CAN.svg`), or
   - **Map** (spatial visualization, e.g. `Access to clean fuels and technologies for cooking, Canada, 1990.svg`).
3. Extracts the **country ISO3 code** (e.g. `CAN`, `BRA`) whenever possible.
4. Aggregates data per country and writes:
   - One JSON file **per country code**, containing two lists: `graphs` and `maps`.
   - One **global summary JSON** with statistics for all countries:
     - ISO3 code
     - Country name
     - Number of graphs
     - Number of maps

This document is a step‑by‑step implementation plan, not the final code.

---

## 1. Requirements and Assumptions

### 1.1 Technical requirements

- Python 3.10+ (or similar recent version).
- Ability to make HTTPS requests to:
  - `https://commons.wikimedia.org/w/api.php`
- Basic file system access to:
  - Write JSON files to a chosen output directory.

### 1.2 Libraries

Use only standard libraries plus `requests`:

- `requests` – HTTP calls to MediaWiki API.
- `json` – read/write JSON.
- `re` – regular expressions for filename parsing.
- `pathlib` – filesystem paths.
- `typing` – type hints.
- `logging` – structured logging.

_All other dependencies are optional._

### 1.3 Data assumptions

1. All files of interest are in:
   - `Category:Uploaded_by_OWID_importer_tool`.
2. Graph filenames generally follow this pattern:

   ```text
   <indicator>, <start_year> to <end_year>, <ISO3>.svg
   ```

   Example:

   ```text
   Agriculture share gdp, 1997 to 2021, CAN.svg
   ```

3. Map filenames generally follow this pattern:

   ```text
   <indicator>, <region_or_country>, <year>.svg
   ```

   Example:

   ```text
   Access to clean fuels and technologies for cooking, Canada, 1990.svg
   ```

   (If the region is a continent like "Africa", those files will not be assigned to a specific country code and may be stored separately or ignored for per‑country JSONs.)

4. You have a dictionary `OWID_COUNTRY_CODES` of the form:

   ```python
   OWID_COUNTRY_CODES = {
       "Afghanistan": "AFG",
       "Åland-Islands": "ALA",
       ...
       "Yemen": "YEM",
       "Zambia": "ZMB",
       "Zimbabwe": "ZWE",
   }
   ```

   From this, you can build helper mappings, e.g. `ISO3 -> Country name`.

---

## 2. Directory and File Layout

Proposed structure:

```text
project_root/
├─ owid_country_codes.py      # Contains OWID_COUNTRY_CODES dict
├─ fetch_commons_files.py     # Main script (or package)
├─ output/
│  ├─ countries/
│  │  ├─ CAN.json
│  │  ├─ BRA.json
│  │  ├─ ...
│  └─ owid_summary.json
└─ logs/
   └─ fetch_commons.log
```

- `output/countries/ISO3.json`: One JSON per country code.
- `output/owid_summary.json`: Aggregated statistics over all countries.
- `logs/fetch_commons.log`: Optional log file for debugging.

---

## 3. Data Models

### 3.1 Country JSON structure (per ISO3 file)

File path example: `output/countries/CAN.json`

```json
{
  "iso3": "CAN",
  "country": "Canada",
  "graphs": [
    {
      "title": "File:Agriculture share gdp, 1997 to 2021, CAN.svg",
      "indicator": "Agriculture share gdp",
      "start_year": 1997,
      "end_year": 2021,
      "file_page": "https://commons.wikimedia.org/wiki/File:Agriculture_share_gdp,_1997_to_2021,_CAN.svg"
    }
  ],
  "maps": [
    {
      "title": "File:Access to clean fuels and technologies for cooking, Canada, 1990.svg",
      "indicator": "Access to clean fuels and technologies for cooking",
      "year": 1990,
      "region": "Canada",
      "file_page": "https://commons.wikimedia.org/wiki/File:Access_to_clean_fuels_and_technologies_for_cooking,_Canada,_1990.svg"
    }
  ]
}
```

Notes:

- `graphs` and `maps` are both lists.
- `indicator` is the textual part before the first comma.
- `file_page` is the full Commons page URL.

### 3.2 Global summary JSON structure

File path: `output/owid_summary.json`

```json
[
  {
    "iso3": "CAN",
    "country": "Canada",
    "graph_count": 123,
    "map_count": 45
  },
  {
    "iso3": "BRA",
    "country": "Brazil",
    "graph_count": 210,
    "map_count": 60
  }
]
```

This is a list of objects, one per ISO3 country code that has at least one graph or map.

---

## 4. MediaWiki API Integration

### 4.1 API endpoint and base parameters

- Endpoint: `https://commons.wikimedia.org/w/api.php`
- Use `action=query` with `list=categorymembers`.

Base parameters for each request:

```python
params = {
    "action": "query",
    "format": "json",
    "list": "categorymembers",
    "cmtitle": "Category:Uploaded_by_OWID_importer_tool",
    "cmtype": "file",
    "cmlimit": "max"
}
```

### 4.2 Pagination with `cmcontinue`

The category contains tens of thousands of files, so you must:

1. Initialize `cmcontinue` to `None`.
2. Request:

   - If `cmcontinue` is not `None`, add to params:
     `params["cmcontinue"] = cmcontinue`

3. After each response:
   - Extract the `categorymembers` list.
   - Append them to a global `all_files` list.
   - If `continue` and `cmcontinue` are present in the response, update `cmcontinue` and repeat.
   - If no `continue` block is present, stop.

Pseudo‑logic:

```text
cmcontinue = None
all_files = []

while True:
    response = call_api(cmcontinue)
    all_files += response["query"]["categorymembers"]

    if "continue" in response:
        cmcontinue = response["continue"]["cmcontinue"]
    else:
        break
```

Each `categorymembers` item has at least:

```json
{
  "pageid": 12345678,
  "ns": 6,
  "title": "File:Something.svg"
}
```

---

## 5. Filename Parsing and Classification

### 5.1 Normalization helper

Create a helper to strip `File:` prefix and `.svg` suffix:

```text
normalize_name(title) -> base_name
```

- Input: `"File:Agriculture share gdp, 1997 to 2021, CAN.svg"`
- Output: `"Agriculture share gdp, 1997 to 2021, CAN"`

### 5.2 Graph detection (time series per country)

Pattern characteristics:

- Contains `" to "` between two 4‑digit years.
- Ends with `, ISO3.svg` where `ISO3` is 3 letters.

Example regex (applied to the full title including `.svg`):

```text
GRAPH_PATTERN = r",\s*(\d{4})\s+to\s+(\d{4}),\s*([A-Z]{3})\.svg$"
```

Captured groups:

1. `start_year` – e.g. `1997`
2. `end_year` – e.g. `2021`
3. `iso3` – e.g. `CAN`

Classification logic:

1. Try matching `GRAPH_PATTERN`.
2. If it matches:
   - `file_type = "graph"`
   - Extract `indicator` as the substring before the first comma.
   - Extract `iso3`, `start_year`, `end_year`.

### 5.3 Map detection (single year, region or country)

Pattern characteristics:

- Ends with `, <region_or_country>, <year>.svg`.
- No `" to "` between years.
- `<year>` is a single 4‑digit year.

Example regex:

```text
MAP_PATTERN = r",\s*([A-Za-z \-\(\)]+),\s*(\d{4})\.svg$"
```

Captured groups:

1. `region_or_country` – e.g. `Canada` or `Africa`.
2. `year` – e.g. `1990`.

Classification logic:

1. Only tested if `GRAPH_PATTERN` did not match.
2. If matches:
   - `file_type = "map"`
   - Extract `indicator` as substring before first comma.
   - Extract `region` and `year`.

### 5.4 Country code resolution

To attach entries to country JSON files, derive ISO3 codes:

1. For **graphs**:
   - ISO3 comes from the graph regex (`([A-Z]{3})`).
   - Use directly.

2. For **maps**:
   - Try to interpret `region_or_country` as a country.
   - Use a lookup table:

     - Normalize the region string (trim spaces, consistent case).
     - Check if it exists as a key in `OWID_COUNTRY_CODES`:
       - If yes, `iso3 = OWID_COUNTRY_CODES[region]`.
       - If not, skip for per‑country aggregation OR store in a separate `other_regions` collection.

3. If an ISO3 code cannot be determined:
   - Do not add that file to any country JSON.
   - Optionally log a warning.

---

## 6. In‑Memory Aggregation

### 6.1 Main aggregation structure

Use a dictionary keyed by ISO3 code:

```text
countries = {
    "CAN": {
        "iso3": "CAN",
        "country": "Canada",
        "graphs": [ ... ],
        "maps": [ ... ]
    },
    "BRA": {
        "iso3": "BRA",
        "country": "Brazil",
        "graphs": [ ... ],
        "maps": [ ... ]
    },
    ...
}
```

### 6.2 Graph entry structure

For `file_type == "graph"` and a known ISO3:

```text
graph_entry = {
    "title": full_file_title,
    "indicator": indicator_name,
    "start_year": start_year_int,
    "end_year": end_year_int,
    "file_page": commons_page_url
}
```

- `commons_page_url` can be built simply as:

  ```text
  "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")
  ```

### 6.3 Map entry structure

For `file_type == "map"` and a known ISO3:

```text
map_entry = {
    "title": full_file_title,
    "indicator": indicator_name,
    "year": year_int,
    "region": region_string,   # often equals country name
    "file_page": commons_page_url
}
```

### 6.4 Aggregation algorithm

For each file (`pageid`, `title`) in `all_files`:

1. Determine `file_type` using the regex rules.
2. If `file_type == "graph"`:
   - Extract `iso3`, `start_year`, `end_year`, `indicator`.
3. If `file_type == "map"`:
   - Extract `region`, `year`, `indicator`.
   - Resolve ISO3 from `region` using `OWID_COUNTRY_CODES`.
4. If no ISO3 can be resolved, skip for per‑country storage.
5. If ISO3 is known:
   - Ensure `countries[iso3]` is initialized with:
     - `iso3`
     - `country` (reverse lookup from ISO3)
     - empty `graphs` and `maps` lists (if not yet created).
   - Append the corresponding entry to either `graphs` or `maps`.

---

## 7. Writing JSON Output

### 7.1 Per‑country JSON files

For each ISO3 code in `countries`:

1. Build the file path:

   ```text
   output_path = output_dir / "countries" / f"{iso3}.json"
   ```

2. Write the JSON with UTF‑8 encoding and indentation:

   ```text
   {
       "iso3": "...",
       "country": "...",
       "graphs": [ ... ],
       "maps": [ ... ]
   }
   ```

3. Overwrite any existing file (or make this configurable).

### 7.2 Global summary JSON

Build a separate list from `countries`:

```text
summary = []

for iso3, data in countries.items():
    summary.append({
        "iso3": iso3,
        "country": data["country"],
        "graph_count": len(data["graphs"]),
        "map_count": len(data["maps"])
    })
```

Write `summary` to:

```text
output/owid_summary.json
```

with indentation.

---

## 8. Logging, Error Handling, and Resilience

### 8.1 Logging

- Initialize a `logging` configuration:
  - INFO for normal progress.
  - WARNING for files that cannot be classified or resolved to a country.

Key log messages:

- Start and end of API fetch.
- Number of files fetched.
- Number of pages (API continuations) processed.
- Count of:
  - `file_type = graph`
  - `file_type = map`
  - unknown type
  - files with unresolved region/country.

### 8.2 Error handling

- Network errors:
  - Wrap API calls in try/except.
  - Optional simple retry mechanism with small sleep.
- JSON parsing errors:
  - Log and abort or skip batch.
- Files that do not match either pattern:
  - Mark as `file_type = "unknown"`.
  - Log for future inspection.

### 8.3 Resumability (optional)

For a very large category:

- Option 1: Save a temporary checkpoint file with:
  - The last `cmcontinue` value.
  - Partially accumulated `countries` data.
- Option 2: Fetch all `all_files` first and write to a JSON file.
  - Then run a second script that parses filenames and writes per‑country JSONs.
  - This separates “data download” and “data processing”.

---

## 9. Validation and Quality Checks

Before relying on the output:

1. **Spot‑check** several countries:
   - Open a few JSON files (`CAN.json`, `BRA.json`) and manually verify:
     - The number of graphs and maps seems reasonable.
     - Example titles exist and are correct.
     - ISO3 code and country name match expectations.

2. **Cross‑check counts**:
   - Compare:
     - Total number of graph entries across all countries.
     - Total number of map entries across all countries.
   - Ensure they roughly match the count of classifiable files from the category.

3. **Edge cases**:
   - Files whose titles do not have clear country/region.
   - Files that use slightly different patterns (e.g. additional commas).

---

## 10. Future Extensions

Once the basic pipeline works, you can extend it with:

1. **Write CSV summary**:
   - In addition to JSON, export a CSV file with `iso3, country, graph_count, map_count`.

2. **Per‑indicator statistics**:
   - Within each country, compute counts per indicator.

3. **Automatic Commons categorization**:
   - Use the resulting JSONs as input to a Pywikibot script that:
     - Adds categories like `Category:Our World in Data graphs of Canada` to the relevant graph files only.

4. **Support for regional JSONs**:
   - Add a similar mechanism for pure regional maps (e.g. Africa, Asia) that have no specific ISO3 code.

**Important Note:**
Always include a clear and descriptive **User-Agent header** in every HTTP request to the MediaWiki API.
Requests without a proper User-Agent may be throttled or blocked by Wikimedia servers.
Use a format that identifies your script, version, and a contact method (e.g., email or wiki username).

**Placeholder User-Agent Example:**
`User-Agent: OWID-Commons-Processor/1.0 (contact: your-email@example.com)`
