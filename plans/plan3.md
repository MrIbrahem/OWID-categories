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

1. United States
2. United Kingdom
3. United Arab Emirates
4. Czech Republic
5. Dominican Republic
6. Central African Republic
7. Philippines
8. Maldives
9. Seychelles
10. Bahamas
11. Marshall Islands
12. Solomon Islands
13. Comoros
14. Gambia
15. Vatican City

**Note:** "Vatican" in the OWID country codes mapping should be treated as "Vatican City" for normalization purposes.

### Rule 2 — Transformation

- If `{Country}` is in the list above: `{Country}` → `the {Country}`
- Otherwise, use the name as is.

### Rule 3 — Category Construction

Always generate:
```
Category:Our World in Data graphs of {NormalizedCountry}
```

**Examples:**
- `Category:Our World in Data graphs of the United States`
- `Category:Our World in Data graphs of the Philippines`
- `Category:Our World in Data graphs of Brazil`
- `Category:Our World in Data graphs of the United Kingdom`
- `Category:Our World in Data graphs of Canada`

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
        country: Country name (e.g., "United States", "Canada")
        
    Returns:
        Normalized country name (e.g., "the United States", "Canada")
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
   - Example: `"United States"` → `"the United States"` → `"Category:Our World in Data graphs of the United States"`

2. **`ensure_category_exists(site, country, dry_run)`**
   - The country parameter should already be normalized when passed to this function
   - The function will use the normalized name in edit summaries

3. **`process_country_file(site, file_path, dry_run, graphs_only)`**
   - Normalize the country name after loading from JSON
   - Use the normalized name throughout the function

### 2.3 Logging and Output

All log messages should use the normalized country name:
- `"Processing USA (the United States): 123 graphs"`
- `"Created category page: Category:Our World in Data graphs of the Philippines"`
- Edit summaries: `"Create category for the United States OWID graphs (automated)"`

---

## 3. Testing Strategy

### 3.1 Unit Tests

Add tests to `tests/test_categorize.py`:

1. **Test normalization function:**
   - Countries requiring "the": United States, Philippines, Bahamas, etc.
   - Countries not requiring "the": Canada, Brazil, Germany, etc.
   - Edge cases: Vatican → Vatican City

2. **Test category name construction:**
   - Verify that `build_category_name()` produces correct output with normalized names
   - Examples:
     - `"United States"` → `"Category:Our World in Data graphs of the United States"`
     - `"Canada"` → `"Category:Our World in Data graphs of Canada"`

### 3.2 Integration Tests

Test with actual country JSON files:
- Load country data for USA, UK, Philippines
- Verify that category names are correctly generated with "the" prefix
- Verify that other countries remain unchanged

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
   - Test normalization function with all 15 special countries
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

### Before (Current):
```
Category:Our World in Data graphs of United States
Category:Our World in Data graphs of Philippines
Category:Our World in Data graphs of United Kingdom
```

### After (With normalization):
```
Category:Our World in Data graphs of the United States
Category:Our World in Data graphs of the Philippines
Category:Our World in Data graphs of the United Kingdom
```

### Unchanged:
```
Category:Our World in Data graphs of Canada
Category:Our World in Data graphs of Brazil
Category:Our World in Data graphs of Germany
```

---

## 6. Special Considerations

### 6.1 Vatican Handling

The OWID country codes dictionary uses `"Vatican"`, but for proper English normalization, we should:
1. Recognize "Vatican" as requiring "the"
2. Potentially expand it to "the Vatican City" for consistency
3. However, to maintain compatibility with existing data, we'll normalize "Vatican" to "the Vatican"

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

- [ ] Normalization function correctly handles all 15 special countries
- [ ] Category names are correctly formatted with "the" prefix
- [ ] Edit summaries use normalized names
- [ ] Log messages use normalized names
- [ ] Existing tests pass
- [ ] New tests cover all special cases
- [ ] Dry-run mode shows correct output
- [ ] Documentation is updated if needed
- [ ] No regressions in existing functionality

---

## 8. Future Enhancements

Potential future improvements:
1. Add configuration file for normalization rules
2. Support for regional variations (e.g., "the Netherlands" in some contexts)
3. Automated migration tool to update existing categories
4. Validation tool to check consistency across all categories
