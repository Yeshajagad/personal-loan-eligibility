"""Run every profile in data/test_profiles.json and write the results to outputs/.

Outputs:
  outputs/profile_results.md      readable result for each profile
  outputs/profile_results.json    the same results as data
  outputs/rejection_stats.md      which rule rejects the most (lender, profile) pairs
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from .common import DATA_DIR
from .engine import decide, format_decision, reason_text
from .models import Applicant
from .rules import load_all

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules-file", default="lender_rules.csv",
                        help="rules file inside data/ (default: lender_rules.csv)")
    args = parser.parse_args()

    with open(DATA_DIR / "test_profiles.json", encoding="utf-8") as f:
        cases = json.load(f)
    lenders = load_all(args.rules_file)

    md = [f"# Test profile results\n\nRules file used: `data/{args.rules_file}`  \n"
          f"Profiles: {len(cases)}\n"]
    results_json = []
    reason_pairs = Counter()      # reason -> number of (profile, lender) rejections containing it
    missing_pairs = 0
    not_eligible_profiles = []
    total_pairs = 0

    for case in cases:
        applicant = Applicant(**case["profile"])
        decision = decide(applicant, lenders)
        md.append(f"## {case['id']}\n\n_{case['description']}_\n")
        md.append("Input: `" + json.dumps(case["profile"]) + "`\n")
        md.append("```\n" + format_decision(applicant, decision) + "\n```\n")

        for r in decision.approvals + decision.rejections:
            total_pairs += 1
        for r in decision.rejections:
            codes = set(r.reasons)
            if any(c.startswith("missing_rule:") for c in codes):
                missing_pairs += 1
                continue
            for code in codes:
                reason_pairs[code] += 1
        if not decision.eligible:
            not_eligible_profiles.append(case["id"])

        results_json.append({
            "id": case["id"], "description": case["description"], "input": case["profile"],
            "eligible": decision.eligible,
            "best": decision.best.lender_name if decision.best else None,
            "approvals": [{"lender": r.lender_name, "max_amount": r.max_amount,
                           "rate_pct": r.rate_pct, "tenure_months": [r.tenure_min_months, r.tenure_max_months],
                           "covers_request": r.covers_request} for r in decision.approvals],
            "rejections": [{"lender": r.lender_name, "reasons": r.reasons} for r in decision.rejections],
        })

    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "profile_results.md").write_text("\n".join(md), encoding="utf-8")
    (OUTPUT_DIR / "profile_results.json").write_text(json.dumps(results_json, indent=2), encoding="utf-8")

    stats = ["# Rejection statistics\n",
             f"Profiles run: {len(cases)}; (profile, lender) pairs: {total_pairs}; "
             f"pairs skipped because a core rule is missing: {missing_pairs}\n",
             f"Profiles with no approving lender: {len(not_eligible_profiles)} "
             f"({', '.join(not_eligible_profiles) or 'none'})\n",
             "| Rejection reason | (profile, lender) pairs |", "|---|---|"]
    for code, n in reason_pairs.most_common():
        stats.append(f"| {reason_text(code)} | {n} |")
    (OUTPUT_DIR / "rejection_stats.md").write_text("\n".join(stats) + "\n", encoding="utf-8")

    print(f"Wrote outputs/profile_results.md, profile_results.json, rejection_stats.md "
          f"({len(cases)} profiles, {missing_pairs} pairs skipped for missing rules)")


if __name__ == "__main__":
    main()
