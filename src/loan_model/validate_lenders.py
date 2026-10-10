"""Checks data/lenders.csv: 20 lenders, every field filled, valid URLs and dates."""
import sys
from collections import Counter

from .common import DATA_DIR, check_date, read_csv

REQUIRED_COLUMNS = [
    "lender_id", "lender_name", "lender_type", "official_product_url",
    "selection_basis", "selection_source_url", "date_read",
]
LENDER_TYPES = {"bank", "nbfc", "fintech"}


def main():
    columns, rows = read_csv(DATA_DIR / "lenders.csv")
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        return 1

    problems = []
    if len(rows) != 20:
        problems.append(f"expected 20 lenders, found {len(rows)}")

    seen_ids = set()
    for line_no, row in enumerate(rows, start=2):  # line 1 is the header
        label = f"line {line_no} ({row['lender_id'] or '?'})"
        for column in REQUIRED_COLUMNS:
            if not row[column]:
                problems.append(f"{label}: '{column}' is empty")
        if row["lender_id"] in seen_ids:
            problems.append(f"{label}: duplicate lender_id")
        seen_ids.add(row["lender_id"])
        if row["lender_type"] and row["lender_type"] not in LENDER_TYPES:
            problems.append(f"{label}: lender_type must be one of {sorted(LENDER_TYPES)}")
        for column in ("official_product_url", "selection_source_url"):
            if row[column] and not row[column].startswith("http"):
                problems.append(f"{label}: '{column}' must start with http")
        if row["date_read"]:
            error = check_date(row["date_read"])
            if error:
                problems.append(f"{label}: date_read {error}")

    type_counts = Counter(r["lender_type"] for r in rows)
    print("Lenders by type:", dict(type_counts))

    if problems:
        for p in problems:
            print(" -", p)
        print(f"{len(problems)} problem(s) found")
        return 1
    print("lenders.csv looks good")
    return 0


if __name__ == "__main__":
    sys.exit(main())
