"""
data_loader.py
--------------
Load and validate product metadata from the Amazon-style JSON dataset.
"""

import json
from pathlib import Path
from typing import List, Dict


def load_products(json_path: str) -> List[Dict]:
    """
    Load product records from a JSON file.

    Args:
        json_path: Path to the JSON file containing product records.

    Returns:
        List of product dictionaries.
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at: {json_path}")

    with open(path, "r") as f:
        products = json.load(f)

    print(f"[DataLoader] Loaded {len(products)} products from {path.name}")
    return products


def filter_by_category(products: List[Dict], keyword: str) -> List[Dict]:
    """
    Filter products whose category contains the given keyword.

    Args:
        products: Full product list.
        keyword:  Category substring to match (case-insensitive).

    Returns:
        Filtered list of products.
    """
    filtered = [
        p for p in products
        if keyword.lower() in p.get("category", "").lower()
    ]
    print(f"[DataLoader] Filtered to {len(filtered)} products matching '{keyword}'")
    return filtered


def validate_product(product: Dict) -> bool:
    """
    Check that a product dict has the required fields.

    Required fields: asin, title, category, brand, color
    """
    required = ["asin", "title", "category", "brand", "color"]
    return all(field in product for field in required)


def get_valid_products(products: List[Dict]) -> List[Dict]:
    """Return only products that pass validation."""
    valid = [p for p in products if validate_product(p)]
    skipped = len(products) - len(valid)
    if skipped:
        print(f"[DataLoader] Skipped {skipped} invalid products.")
    return valid


# ── Quick sanity check ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import os

    script_dir = Path(__file__).parent.parent
    data_path = script_dir / "data" / "sample_products.json"

    products = load_products(str(data_path))
    valid = get_valid_products(products)

    print("\nSample product:")
    import pprint
    pprint.pprint(valid[0])
