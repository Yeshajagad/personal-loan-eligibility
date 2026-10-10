from src.loan_model.fill_gaps import fill


def row(lid, rule, value, applies="all", status="listed"):
    return {"lender_id": lid, "rule_name": rule, "value": str(value), "unit": "x", "applies_to": applies,
            "city_group": "all", "rule_status": status, "source_url": "u", "date_read": "2026-10-10",
            "evidence_note": "synthetic-test-fixture"}


LENDERS = [{"lender_id": "A", "lender_type": "bank", "official_product_url": "http://a"},
           {"lender_id": "B", "lender_type": "bank", "official_product_url": "http://b"},
           {"lender_id": "C", "lender_type": "bank", "official_product_url": "http://c"}]


def base(lid):
    return [row(lid, "employment_types_allowed", "salaried"), row(lid, "max_loan_amount", 100000),
            row(lid, "rate_min_pct", 10)]


def test_missing_rule_gets_estimated_row():
    rules = base("A") + [row("B", "min_age", 21), row("B", "max_foir_pct", 50)] + base("B")[:0]
    out, policy, skipped = fill(rules, LENDERS, "2026-10-10")
    est = [r for r in out if r["lender_id"] == "A" and r["rule_status"] == "estimated"]
    assert any(r["rule_name"] == "max_foir_pct" for r in est)
    assert all("Estimated" in r["evidence_note"] or "estimated" in r["evidence_note"] for r in est)


def test_lender_without_max_loan_or_rate_is_skipped():
    rules = base("A") + [row("B", "employment_types_allowed", "salaried"), row("B", "min_age", 21)]
    out, policy, skipped = fill(rules, LENDERS, "2026-10-10")
    assert "B" in skipped and "C" in skipped
    assert not [r for r in out if r["lender_id"] == "B" and r["rule_status"] == "estimated"]
