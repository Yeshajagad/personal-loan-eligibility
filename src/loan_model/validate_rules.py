"""Checks data/lender_rules.csv and reports coverage per lender."""
import argparse
import sys
from collections import Counter, defaultdict

from .catalog import APPLIES_TO, CITY_GROUPS, CORE_RULES, RULE_CATALOG, RULE_STATUSES, TEXT_RULES
from .common import DATA_DIR, check_date, read_csv

RULE_COLUMNS = [
    "lender_id", "rule_name", "value", "unit", "applies_to", "city_group",
    "rule_status", "source_url", "date_read", "evidence_note",
]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="also fail when a lender is missing a core rule")
    parser.add_argument("--file", default="lender_rules.csv",
                        help="rules file inside data/ (default: lender_rules.csv)")
    args = parser.parse_args(argv)

    _, lender_rows = read_csv(DATA_DIR / "lenders.csv")
    lender_ids = [r["lender_id"] for r in lender_rows]
    columns, rows = read_csv(DATA_DIR / args.file)
    missing_columns = [c for c in RULE_COLUMNS if c not in columns]
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        return 1

    problems = []
    seen_keys = set()
    rules_by_lender = defaultdict(set)
    status_by_lender = defaultdict(Counter)

    for line_no, row in enumerate(rows, start=2):
        label = f"line {line_no} ({row['lender_id']}/{row['rule_name']})"
        if row["lender_id"] not in lender_ids:
            problems.append(f"{label}: lender_id is not in lenders.csv")
        name = row["rule_name"]
        if name not in RULE_CATALOG:
            problems.append(f"{label}: unknown rule_name")
            continue
        if row["applies_to"] not in APPLIES_TO:
            problems.append(f"{label}: applies_to must be one of {sorted(APPLIES_TO)}")
        if row["city_group"] not in CITY_GROUPS:
            problems.append(f"{label}: city_group must be one of {sorted(CITY_GROUPS)}")
        if row["rule_status"] not in RULE_STATUSES:
            problems.append(f"{label}: rule_status must be one of {sorted(RULE_STATUSES)}")
        if row["unit"] != RULE_CATALOG[name]["unit"]:
            problems.append(f"{label}: unit should be '{RULE_CATALOG[name]['unit']}'")

        if name in TEXT_RULES:
            if not row["value"]:
                problems.append(f"{label}: value is empty")
        else:
            try:
                float(row["value"])
            except ValueError:
                problems.append(f"{label}: value must be a number")

        if not row["source_url"].startswith("http"):
            problems.append(f"{label}: source_url must start with http")
        error = check_date(row["date_read"])
        if error:
            problems.append(f"{label}: date_read {error}")

        min_note = 30 if row["rule_status"] in ("derived", "estimated") else 10
        if len(row["evidence_note"]) < min_note:
            problems.append(f"{label}: evidence_note too short (explain where found or how derived/estimated)")

        key = (row["lender_id"], name, row["applies_to"], row["city_group"])
        if key in seen_keys:
            problems.append(f"{label}: duplicate rule for the same lender/applies_to/city_group")
        seen_keys.add(key)

        rules_by_lender[row["lender_id"]].add(name)
        status_by_lender[row["lender_id"]][row["rule_status"]] += 1

    print(f"{'lender':<12}{'rules':>6}{'listed':>8}{'derived':>9}{'estimated':>11}  missing core rules")
    gaps = 0
    for lender_id in lender_ids:
        counts = status_by_lender[lender_id]
        missing = [r for r in CORE_RULES if r not in rules_by_lender[lender_id]]
        gaps += len(missing)
        print(f"{lender_id:<12}{sum(counts.values()):>6}{counts['listed']:>8}"
              f"{counts['derived']:>9}{counts['estimated']:>11}  {', '.join(missing) or '-'}")

    for p in problems:
        print(" -", p)
    print(f"\n{len(rows)} rule rows, {len(problems)} row problem(s), {gaps} missing core rule(s)")
    if problems or (args.strict and gaps):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
