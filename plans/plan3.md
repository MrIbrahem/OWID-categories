# Plan 3: Country Name Normalization with "the" Prefix

## 0. Overview

When generating category names such as:
```
Category:Our World in Data graphs of {Country}
```

The agent must ensure that the country name is written correctly in English, adding "the" only for countries that require it.

This plan documents the rules for normalizing country names and the implementation approach.

---

## 1. Rules for Country Name Normalization

### Rule 1 — Countries that require "the"

Add **"the"** only if the country name is one of:

1. Democratic Republic of Congo
2. Dominican Republic
3. Philippines
4. Netherlands
5. United Arab Emirates
6. United Kingdom
7. United States
8. Czech Republic
9. Central African Republic
10. Maldives
11. Seychelles
12. Bahamas
13. Marshall Islands
14. Solomon Islands
15. Comoros
16. Gambia
17. Vatican City

**Note:** This is the definitive list based on proper English grammar conventions for country names as used in categorization.

### Rule 2 — Transformation

- If `{Country}` is in the list above: `{Country}` → `the {Country}`
- Otherwise, use the name as is.

### Rule 3 — Category Construction

Always generate:
```
Category:Our World in Data graphs of {NormalizedCountry}
```

**Examples:**
- `Category:Our World in Data graphs of the United Kingdom`
- `Category:Our World in Data graphs of the United States`
- `Category:Our World in Data graphs of the Philippines`
- `Category:Our World in Data graphs of the Netherlands`
- `Category:Our World in Data graphs of the Dominican Republic`
- `Category:Our World in Data graphs of the United Arab Emirates`
- `Category:Our World in Data graphs of the Democratic Republic of Congo`
- `Category:Our World in Data graphs of the Czech Republic`
- `Category:Our World in Data graphs of the Bahamas`
- `Category:Our World in Data graphs of Brazil` (no "the")
- `Category:Our World in Data graphs of Canada` (no "the")

### Rule 4 — Consistency

Apply the same normalized name in:
- Category titles
- Edit summaries
- Logs
- All generated text

---

## 2. Implementation Approach

### 2.1 New Function

Create a new function `normalize_country_name(country: str) -> str` in `src/categorize_commons_files.py`:

```python
def normalize_country_name(country: str) -> str:
    """
    Normalize country name by adding "the" prefix where appropriate.

    Args:
        country: Country name (e.g., "United Kingdom", "Canada")

    Returns:
        Normalized country name (e.g., "the United Kingdom", "Canada")
    """
```

This function will:
1. Define a set of countries that require "the" prefix
2. Check if the input country is in this set
3. Return "the {country}" if it requires the prefix
4. Return the country name unchanged otherwise

### 2.2 Modified Functions

Update the following existing functions to use the normalized country name:

1. **`build_category_name(country: str) -> str`**
   - Call `normalize_country_name()` before constructing the category name
   - Example: `"United Kingdom"` → `"the United Kingdom"` → `"Category:Our World in Data graphs of the United Kingdom"`

2. **`ensure_category_exists(site, country, dry_run)`**
   - The country parameter should already be normalized when passed to this function
   - The function will use the normalized name in edit summaries

3. **`process_files(site, file_path, dry_run, graphs_only)`**
   - Normalize the country name after loading from JSON
   - Use the normalized name throughout the function

### 2.3 Logging and Output

All log messages should use the normalized country name:
- `"Processing GBR (the United Kingdom): 123 graphs"`
- `"Processing USA (the United States): 45 graphs"`
- `"Created category page: Category:Our World in Data graphs of the Philippines"`
- Edit summaries: `"Create category for the United Kingdom OWID graphs (automated)"`

---

## 3. Testing Strategy

### 3.1 Unit Tests

Add tests to `tests/test_categorize.py`:

1. **Test normalization function:**
   - Countries requiring "the": United Kingdom, United States, Philippines, Netherlands, Bahamas, etc.
   - Countries not requiring "the": Canada, Brazil, Germany, France, etc.

2. **Test category name construction:**
   - Verify that `build_category_name()` produces correct output with normalized names
   - Examples:
     - `"United Kingdom"` → `"Category:Our World in Data graphs of the United Kingdom"`
     - `"United States"` → `"Category:Our World in Data graphs of the United States"`
     - `"Canada"` → `"Category:Our World in Data graphs of Canada"`

### 3.2 Integration Tests

Test with actual country JSON files:
- Load country data for UK (United Kingdom), USA (United States), Philippines, Netherlands
- Verify that category names are correctly generated with "the" prefix
- Verify that other countries (like Canada, Brazil) remain unchanged (no "the")

---

## 4. Implementation Steps

1. **Add normalization function** to `src/categorize_commons_files.py`
   - Define the list of countries requiring "the"
   - Implement the normalization logic

2. **Update `build_category_name()`**
   - Call `normalize_country_name()` before constructing category

3. **Update all usage points**
   - Ensure normalized names are used in edit summaries
   - Ensure normalized names are used in log messages

4. **Add unit tests**
   - Test normalization function with all 17 countries requiring "the"
   - Test with regular countries
   - Test category name construction

5. **Run existing tests**
   - Ensure no regressions in existing functionality
   - Update test expectations if needed

6. **Manual verification**
   - Test with dry-run mode
   - Verify output logs show correct normalization
   - Check that category names match expected format

---

## 5. Example Output

### Before (Without normalization):
```
Category:Our World in Data graphs of United Kingdom
Category:Our World in Data graphs of United States
Category:Our World in Data graphs of Philippines
Category:Our World in Data graphs of Netherlands
Category:Our World in Data graphs of Dominican Republic
```

### After (With normalization):
```
Category:Our World in Data graphs of the United Kingdom
Category:Our World in Data graphs of the United States
Category:Our World in Data graphs of the Philippines
Category:Our World in Data graphs of the Netherlands
Category:Our World in Data graphs of the Dominican Republic
Category:Our World in Data graphs of the United Arab Emirates
Category:Our World in Data graphs of the Democratic Republic of Congo
Category:Our World in Data graphs of the Czech Republic
Category:Our World in Data graphs of the Bahamas
```

### Unchanged (Countries not in the list):
```
Category:Our World in Data graphs of Canada
Category:Our World in Data graphs of Brazil
Category:Our World in Data graphs of Germany
Category:Our World in Data graphs of France
```

---

## 6. Special Considerations

### 6.1 Democratic Republic of Congo

The OWID country codes dictionary uses `"Democratic Republic of Congo"` (not "Democratic Republic of the Congo"). The normalization adds "the" prefix to this existing name.

### 6.2 Backward Compatibility

This change affects:
- Category names on Wikimedia Commons
- If categories have already been created with the old format, they may need manual cleanup
- The script should handle both old and new formats when checking if a category already exists

### 6.3 Data Integrity

The normalization happens at categorization time (Phase 2), not during data fetching (Phase 1):
- Phase 1 JSON files continue to store original country names from `owid_country_codes.py`
- Phase 2 normalizes these names when creating categories
- This separation ensures data integrity and allows easy updates to normalization rules

---

## 7. Validation Checklist

Before completing implementation:

- [x] Normalization function correctly handles all 17 countries requiring "the"
- [x] Category names are correctly formatted with "the" prefix
- [x] Edit summaries use normalized names
- [x] Log messages use normalized names
- [x] Existing tests pass
- [x] New tests cover all special cases
- [x] Dry-run mode shows correct output
- [x] Documentation is updated
- [x] No regressions in existing functionality

---

## 8. Future Enhancements

Potential future improvements:
1. Add configuration file for normalization rules
2. Automated migration tool to update existing categories if the list changes
3. Validation tool to check consistency across all categories
4. Support for additional language-specific variations if needed
