"""Builds data/lender_rules.csv from data/rules_from_sources.csv.

rules_from_sources.csv holds only what was read on the lender pages. Lenders do not
publish every rule the engine needs (FOIR is the biggest gap), so this script adds an
estimated row for each missing core rule. Nothing is typed in by hand: every fallback
is computed from the published values of the other lenders, and the evidence_note
says exactly how.

A lender is only filled in if its pages gave at least a maximum loan amount and a
starting interest rate (for that employment type). With less than that, the model
would be inventing the lender, so it stays marked as "rule data missing".

Run:  python -m src.loan_model.fill_gaps
"""
import csv
import statistics
from collections import Counter, defaultdict
from datetime import date

from .catalog import CORE_RULES, RULE_CATALOG
from .common import DATA_DIR, read_csv

SOURCE_FILE = "rules_from_sources.csv"
OUTPUT_FILE = "lender_rules.csv"
POLICY_FILE = "gap_filling_values.csv"

COLUMNS = ["lender_id", "rule_name", "value", "unit", "applies_to", "city_group",
           "rule_status", "source_url", "date_read", "evidence_note"]

# rule -> how the fallback is computed from the other lenders' published values
METHODS = {
    "min_age": "mode",
    "max_age_at_maturity": "mode",
    "min_monthly_income": "median",
    "min_credit_score": "min",
    "max_foir_pct": "median",        # computed over every FOIR row, because few lenders state one
    "min_loan_amount": "median",
    "min_tenure_months": "mode",
    "max_tenure_months": "median",
}
REQUIRED_TO_FILL = ("max_loan_amount", "rate_min_pct")


def number(value):
    value = float(value)
    return int(value) if value == int(value) else round(value, 2)


def applies(row, employment):
    return row["applies_to"] in ("all", employment)


def has_rule(rows, rule, employment):
    return any(r["rule_name"] == rule and applies(r, employment) for r in rows)


def rule_value(rows, rule, employment):
    """Value of the best matching row (a row for this employment type beats 'all')."""
    best = None
    for r in rows:
        if r["rule_name"] == rule and applies(r, employment):
            if best is None or (r["applies_to"] != "all"):
                best = r
    return None if best is None else float(best["value"])


def served_types(rows):
    for r in rows:
        if r["rule_name"] == "employment_types_allowed":
            return {p for p in r["value"].split("|") if p}
    return set()


def compute_policy(rule_rows, lender_type):
    """Fallback value for each rule, from the published rows. Returns {rule: (value, method, n)}."""
    policy = {}
    for rule, method in METHODS.items():
        if method == "median" and rule == "max_foir_pct":
            values = [float(r["value"]) for r in rule_rows if r["rule_name"] == rule]
        else:
            values = [float(r["value"]) for r in rule_rows
                      if r["rule_name"] == rule and r["rule_status"] in ("listed", "derived")]
        if not values:
            continue
        if method == "mode":
            counts = Counter(values)
            top = max(counts.values())
            value = min(v for v, c in counts.items() if c == top)
        elif method == "median":
            value = statistics.median(values)
        else:
            value = min(values)
        policy[rule] = (number(value), method, len(values))

    # maximum rate = starting rate + the usual spread for that type of lender
    by_lender = defaultdict(list)
    for r in rule_rows:
        if r["rule_status"] in ("listed", "derived"):
            by_lender[r["lender_id"]].append(r)
    spreads = defaultdict(list)
    for lender_id, rows in by_lender.items():
        low = [float(r["value"]) for r in rows if r["rule_name"] == "rate_min_pct"]
        high = [float(r["value"]) for r in rows if r["rule_name"] == "rate_max_pct"]
        if low and high:
            group = "bank" if lender_type[lender_id] == "bank" else "non-bank"
            spreads[group].append(max(high) - min(low))
    for group, values in spreads.items():
        policy["rate_spread_" + group] = (round(statistics.median(values), 2), "median", len(values))
    return policy


def fill(rule_rows, lender_rows, today):
    """Return (all_rows, policy, skipped) where skipped is {lender_id: reason}."""
    lender_type = {l["lender_id"]: l["lender_type"] for l in lender_rows}
    product_url = {l["lender_id"]: l["official_product_url"] for l in lender_rows}
    policy = compute_policy(rule_rows, lender_type)
    by_lender = defaultdict(list)
    for r in rule_rows:
        by_lender[r["lender_id"]].append(r)

    out = list(rule_rows)
    skipped = {}
    for lender in lender_rows:
        lid = lender["lender_id"]
        rows = by_lender[lid]
        emps = served_types(rows)
        if not emps:
            skipped[lid] = "no readable eligibility information (employment types served unknown)"
            continue
        ok = sorted(e for e in emps if all(has_rule(rows, r, e) for r in REQUIRED_TO_FILL))
        if not ok:
            skipped[lid] = "pages gave no maximum loan amount or starting rate"
            continue

        def add(rule, value, employment_list, note):
            target = "all" if set(employment_list) == emps else None
            for e in ([None] if target else employment_list):
                out.append({
                    "lender_id": lid, "rule_name": rule, "value": str(number(value)),
                    "unit": RULE_CATALOG[rule]["unit"], "applies_to": target or e,
                    "city_group": "all", "rule_status": "estimated",
                    "source_url": product_url[lid], "date_read": today, "evidence_note": note})

        for rule in CORE_RULES:
            if rule == "employment_types_allowed":
                continue
            missing = [e for e in ok if not has_rule(rows, rule, e)]
            if not missing:
                continue
            if rule == "rate_max_pct":
                group = "bank" if lender_type[lid] == "bank" else "non-bank"
                key = "rate_spread_" + group
                if key not in policy:
                    continue
                spread, _, n = policy[key]
                for e in missing:
                    low = rule_value(rows, "rate_min_pct", e)
                    add(rule, low + spread, [e],
                        f"Maximum rate is not published. Estimated as the starting rate {number(low)}% plus "
                        f"{spread} points, the median gap between lowest and highest published rate "
                        f"for {n} {group} lenders")
            elif rule in policy:
                value, method, n = policy[rule]
                add(rule, value, missing,
                    f"Not published by this lender. Estimated as the {method} of {n} published "
                    f"values across lenders in this data set ({value})")
    return out, policy, skipped


def main():
    _, lender_rows = read_csv(DATA_DIR / "lenders.csv")
    _, rule_rows = read_csv(DATA_DIR / SOURCE_FILE)
    today = date.today().isoformat()
    rows, policy, skipped = fill(rule_rows, lender_rows, today)

    order = {l["lender_id"]: i for i, l in enumerate(lender_rows)}
    rows.sort(key=lambda r: order[r["lender_id"]])  # stable: keeps the original order inside a lender
    with open(DATA_DIR / OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    with open(DATA_DIR / POLICY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fallback_name", "value", "method", "number_of_published_values"])
        for name, (value, method, n) in sorted(policy.items()):
            writer.writerow([name, value, method, n])

    print(f"Read {len(rule_rows)} sourced rows, wrote {len(rows)} rows to data/{OUTPUT_FILE} "
          f"({len(rows) - len(rule_rows)} estimated rows added)")
    print("Fallback values used:")
    for name, (value, method, n) in sorted(policy.items()):
        print(f"  {name:<24}{value:>10}   ({method} of {n} published values)")
    for lid, reason in skipped.items():
        print(f"NOT filled: {lid} - {reason}")


if __name__ == "__main__":
    main()
