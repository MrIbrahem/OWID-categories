# Changelog

## 22

-   This pull request introduces functionality to automatically upload the generated wikitext report to a configured Wikimedia page (REPORT_PAGE) using MwClientPage. The feedback highlights a potential crash where site is checked for None only after it has already been used in make_report_data. Additionally, it is recommended to load REPORT_PAGE from an environment variable instead of hardcoding it, and to check and log the return value of page.edit to handle potential upload failures. [#22](https://github.com/MrIbrahem/OWID-categories/pull/22)

## 21

-   This pull request introduces wikitext report generation for country and continent category data, adding a new <code>wikitext_report</code> module, a helper function to fetch subcategory information, and integrating report saving into the main execution flow. Additionally, file classification regex patterns were updated to support more date formats and plain graph patterns. The review feedback highlights several robustness and code quality improvements, including handling potential <code>None</code> values from <code>get_site()</code> to prevent <code>AttributeError</code>, using safe dictionary lookups to avoid <code>KeyError</code>, correcting a typo in the report table header, removing an unused import, fixing a trailing space in a regex pattern, normalizing extracted ISO3 codes to uppercase, and wrapping file writing operations in a try-except block to handle <code>OSError</code> gracefully.. [#21](https://github.com/MrIbrahem/OWID-categories/pull/21)

## 20

-   This pull request restructures the project by modularizing the core codebase into a new <code>src/main_app</code> package, introducing dedicated API services, a wrapper for <code>mwclient</code>, and a centralized logging configuration. The code review identified several important issues and optimization opportunities: adding a timeout and error handling to a synchronous HTTP request in <code>category_members.py</code>, replacing relative imports with absolute imports in the top-level <code>src/test.py</code> script to prevent runtime import errors, merging redundant conditional blocks in <code>main_run_categorize.py</code> for better readability, and converting a list to a set to optimize lookup complexity from O(N) to O(1) during file filtering.. [#20](https://github.com/MrIbrahem/OWID-categories/pull/20)

## 19

-   This pull request updates <code>src/fetch_commons_files.py</code> to load credentials, connect to Wikimedia Commons, and fetch category members using the new <code>get_category_members</code> function. Feedback was provided regarding a potential data loss issue: if the API call fails and returns an empty list, the script could overwrite output files with empty data. It is recommended to abort execution if no files are retrieved and to filter the results by namespace to match the original behavior.. [#19](https://github.com/MrIbrahem/OWID-categories/pull/19)

## 18

-   This pull request refactors the categorization module by extracting wikitext analysis utilities and category redirect resolution logic into separate modules (<code>wikitext_utils.py</code> and <code>category_redirects.py</code>), which improves modularity and testability. Feedback on these changes highlights a critical bug in <code>add_category_to_page</code> where transient retrieval failures could result in overwriting existing page content. Additionally, improvements are suggested to prevent infinite recursion on self-redirects and to make the category existence check more robust by handling MediaWiki space/underscore equivalence and case-insensitivity. [#18](https://github.com/MrIbrahem/OWID-categories/pull/18)

## 17

-   This pull request introduces a new <code>resolve_category_redirect</code> function to handle wiki category redirects, integrating it into the file processing pipeline and adding comprehensive unit tests. Feedback on the changes suggests making the category prefix check more robust by handling case-insensitivity and leading colons, as well as wrapping the page text retrieval in a try-except block to gracefully handle potential network or API exceptions. [#16](https://github.com/MrIbrahem/OWID-categories/pull/16)
