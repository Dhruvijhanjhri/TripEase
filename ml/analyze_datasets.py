"""
Dataset analysis utilities for TripEase ML foundation.

This script is intentionally standalone and does NOT integrate with Django.
It is meant to be run manually from the project root:

    python -m ml.analyze_datasets

It will:
- Inspect specified CSV files under `data/`
- Print column names, row counts, missing values, and simple type hints

NOTE:
- No models are trained here.
- No columns are dropped.
- No categorical encoding is performed.
"""

import csv
import os
from collections import Counter
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


TARGET_FILES = [
    # Currently only easemytrip.csv is present in the repo.
    # The same analysis logic can be reused for future datasets
    # such as flight_delay.csv, airline_on_time.csv, and flight_price.csv
    # once they are added under data/.
    "easemytrip.csv",
]


def infer_column_types(header: List[str], rows: List[List[str]], max_samples: int = 500) -> Dict[str, str]:
    """
    Very lightweight type inference based on sampled non-empty values.
    Types reported are descriptive only (no casting is done).
    """
    types: Dict[str, str] = {}

    for col_idx, col_name in enumerate(header):
        values: List[str] = []
        for r in rows:
            if col_idx >= len(r):
                continue
            v = (r[col_idx] or "").strip()
            if v:
                values.append(v)
            if len(values) >= max_samples:
                break

        if not values:
            types[col_name] = "empty / unknown"
            continue

        is_int = True
        is_float = True
        for v in values:
            try:
                int(v)
            except ValueError:
                is_int = False
            try:
                float(v)
            except ValueError:
                is_float = False
            if not is_int and not is_float:
                break

        if is_int:
            types[col_name] = "integer-like (numeric)"
        elif is_float:
            types[col_name] = "float-like (numeric)"
        else:
            types[col_name] = "string / categorical or datetime-like"

    return types


def analyze_csv(filename: str) -> None:
    path = os.path.join(DATA_DIR, filename)
    print(f"=== {filename} ===")
    if not os.path.exists(path):
        print("STATUS: FILE_NOT_FOUND\n")
        return

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print("STATUS: EMPTY_FILE\n")
        return

    header = rows[0]
    data_rows = rows[1:]

    print(f"Columns ({len(header)}): {header}")
    print(f"Total rows (excluding header): {len(data_rows)}")

    # Missing values
    missing = {h: 0 for h in header}
    for r in data_rows:
        for i, h in enumerate(header):
            v = r[i] if i < len(r) else ""
            if v is None or str(v).strip() == "":
                missing[h] += 1
    print("Missing values per column:")
    for h in header:
        print(f"  {h}: {missing[h]}")

    # Simple type hints
    inferred_types = infer_column_types(header, data_rows)
    print("Inferred column value types (heuristic):")
    for h in header:
        print(f"  {h}: {inferred_types[h]}")

    # Simple data quality hints: extremely skewed missingness
    print("Data quality notes:")
    for h in header:
        miss = missing[h]
        if miss == 0:
            continue
        ratio = miss / max(len(data_rows), 1)
        if ratio > 0.9:
            print(f"  - {h}: ~{ratio:.0%} values missing; likely optional/structural field.")
        elif ratio > 0.3:
            print(f"  - {h}: ~{ratio:.0%} values missing; consider careful handling.")

    print()


def main() -> None:
    print(f"Base dir: {BASE_DIR}")
    print(f"Data dir: {DATA_DIR}")
    print()
    for fname in TARGET_FILES:
        analyze_csv(fname)


if __name__ == \"__main__\":
    main()

