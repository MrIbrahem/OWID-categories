#!/usr/bin/env python3
"""
Example: Using the categorize module directly

This demonstrates how to use the categorize module functions
programmatically without running the full scripts.
"""

from categorize.wiki import (
    load_credentials,
)
from categorize.utils import (
    load_json_file,
    normalize_country_name,
    build_category_name,
    get_parent_category,
)
from owid_config import COUNTRIES_DIR


def example_normalize_countries():
    """Example: Normalize country names."""
    print("=" * 60)
    print("Example: Country Name Normalization")
    print("=" * 60)

    countries = [
        "Canada",
        "United States",
        "United Kingdom",
        "France",
        "Philippines",
        "Netherlands",
    ]

    for country in countries:
        normalized = normalize_country_name(country)
        print(f"{country:25} → {normalized}")
    print()


def example_build_categories():
    """Example: Build category names."""
    print("=" * 60)
    print("Example: Category Name Building")
    print("=" * 60)

    # Countries
    print("\nCountries:")
    for country in ["Canada", "United States", "France"]:
        category = build_category_name(country, "country", "graphs")
        print(f"  {category}")

    # Continents
    print("\nContinents:")
    for continent in ["Africa", "Asia", "Europe"]:
        category = build_category_name(continent, "continent", "graphs")
        print(f"  {category}")
    print()


def example_parent_categories():
    """Example: Get parent categories."""
    print("=" * 60)
    print("Example: Parent Categories")
    print("=" * 60)

    country_parent = get_parent_category("country")
    continent_parent = get_parent_category("continent")

    print(f"Countries parent: {country_parent}")
    print(f"Continents parent: {continent_parent}")
    print()


def example_load_json():
    """Example: Load a JSON file."""
    print("=" * 60)
    print("Example: Load JSON File")
    print("=" * 60)

    # Try to load a sample country file
    sample_file = COUNTRIES_DIR / "CAN.json"

    if sample_file.exists():
        data = load_json_file(sample_file)
        if data:
            print(f"✓ Loaded: {sample_file}")
            print(f"  Country: {data.get('country')}")
            print(f"  ISO3: {data.get('iso3')}")
            print(f"  Graphs: {len(data.get('graphs', []))}")
            print(f"  Maps: {len(data.get('maps', []))}")
    else:
        print(f"✗ File not found: {sample_file}")
        print("  (Run fetch_commons_files.py first)")
    print()


def example_connect_dry_run():
    """Example: Connection test (requires credentials)."""
    print("=" * 60)
    print("Example: Connection Test")
    print("=" * 60)

    # This example checks credentials without actual connection
    username, password = load_credentials()

    if username and password:
        print("✓ Credentials loaded")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password)}")
        print("\n  Note: Use connect_to_commons() to actually connect")
    else:
        print("✗ No credentials found")
        print("  Create .env file with WM_USERNAME and PASSWORD")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "CATEGORIZE MODULE EXAMPLES" + " " * 22 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Run examples
    example_normalize_countries()
    example_build_categories()
    example_parent_categories()
    example_load_json()
    example_connect_dry_run()

    print("=" * 60)
    print("Examples Complete!")
    print("=" * 60)
    print()
    print("To use in your code:")
    print("  from categorize.wiki import connect_to_commons")
    print("  from categorize.utils import normalize_country_name")
    print()


if __name__ == "__main__":
    main()
