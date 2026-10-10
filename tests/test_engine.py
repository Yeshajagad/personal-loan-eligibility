import math

import pytest

from src.loan_model.engine import (
    amount_for_emi, decide, emi_for, evaluate_lender, format_decision, inr,
)
from src.loan_model.models import Applicant
from src.loan_model.rules import build_lender_rules

# SYNTHETIC rules for testing the engine's logic. Not real lender data.
BASE_RULES = {
    "employment_types_allowed": "salaried|self_employed",
    "min_age": 21, "max_age_at_maturity": 60,
    "min_monthly_income": 25000, "min_credit_score": 700,
    "min_total_experience_months": 24, "min_current_job_months": 6,
    "max_foir_pct": 50, "max_income_multiple": 20,
    "min_loan_amount": 50000, "max_loan_amount": 2500000,
    "min_tenure_months": 12, "max_tenure_months": 60,
    "rate_min_pct": 10.5, "rate_max_pct": 24,
}


def make_lender(lender_id="TESTBANK", extra_rows=(), **overrides):
    rules = dict(BASE_RULES)
    for key, value in overrides.items():
        if value is None:
            rules.pop(key)
        else:
            rules[key] = value
    rows = [{"lender_id": lender_id, "rule_name": k, "value": str(v), "applies_to": "all",
             "city_group": "all", "rule_status": "listed", "source_url": "synthetic-test-fixture",
             "date_read": "2026-10-09"} for k, v in rules.items()]
    for extra in extra_rows:
        rows.append({"lender_id": lender_id, "rule_status": "listed",
                     "source_url": "synthetic-test-fixture", "date_read": "2026-10-09", **extra})
    return build_lender_rules([{"lender_id": lender_id, "lender_name": lender_id}], rows)[0]


def make_applicant(**changes):
    base = dict(age_years=30, employment_type="salaried", employer_category="large_private",
                monthly_income_inr=80000, total_experience_months=96, current_job_months=36,
                city="Ahmedabad", credit_score=780, existing_emi_inr=0,
                loan_amount_requested_inr=500000, tenure_requested_months=36)
    base.update(changes)
    return Applicant(**base)


def test_good_applicant_is_approved_with_expected_amount_and_rate():
    result = evaluate_lender(make_applicant(), make_lender())
    expected = math.floor(amount_for_emi(40000, 10.5, 36) / 1000) * 1000
    assert result.approved
    assert result.rate_pct == 10.5          # score 780 >= 750 -> lowest rate
    assert result.max_amount == expected and expected > 1_000_000
    assert result.covers_request and result.tenure_used_months == 36


def test_low_score_rejected():
    result = evaluate_lender(make_applicant(credit_score=650), make_lender())
    assert not result.approved and "credit_score_below_minimum" in result.reasons


def test_no_credit_history_rejected():
    result = evaluate_lender(make_applicant(credit_score=None), make_lender())
    assert "no_credit_history" in result.reasons


def test_high_existing_emi_fails_foir():
    result = evaluate_lender(
        make_applicant(monthly_income_inr=40000, existing_emi_inr=25000), make_lender())
    assert "foir_exceeded" in result.reasons


def test_new_job_rejected():
    result = evaluate_lender(make_applicant(current_job_months=2), make_lender())
    assert "current_job_too_short" in result.reasons


def test_age_near_limit_is_capped_then_rejected():
    near = evaluate_lender(make_applicant(age_years=59, tenure_requested_months=48), make_lender())
    assert near.approved and near.tenure_max_months == 12 and near.tenure_used_months == 12
    too_old = evaluate_lender(make_applicant(age_years=60), make_lender())
    assert "age_too_high_for_minimum_tenure" in too_old.reasons


def test_recent_default_rejected():
    result = evaluate_lender(make_applicant(recent_defaults=True), make_lender())
    assert "recent_default_or_delinquency" in result.reasons


def test_employment_type_not_served():
    lender = make_lender(employment_types_allowed="salaried")
    result = evaluate_lender(make_applicant(employment_type="self_employed"), lender)
    assert result.reasons == ["employment_type_not_served"]


def test_missing_core_rule_is_reported_not_guessed():
    result = evaluate_lender(make_applicant(), make_lender(rate_max_pct=None))
    assert result.reasons == ["missing_rule:rate_max_pct"]


def test_city_specific_income_rule_beats_general_rule():
    metro_row = {"rule_name": "min_monthly_income", "value": "35000",
                 "applies_to": "all", "city_group": "metro"}
    lender = make_lender(extra_rows=[metro_row])
    mumbai = evaluate_lender(make_applicant(monthly_income_inr=30000, city="Mumbai"), lender)
    jaipur = evaluate_lender(make_applicant(monthly_income_inr=30000, city="Jaipur"), lender)
    assert "income_below_minimum" in mumbai.reasons
    assert jaipur.approved


def test_best_option_is_lowest_rate_among_lenders_covering_request():
    cheap = make_lender("CHEAP", rate_min_pct=10.0)
    pricey = make_lender("PRICEY", rate_min_pct=14.0)
    decision = decide(make_applicant(), [pricey, cheap])
    assert decision.eligible and decision.best.lender_id == "CHEAP"
    assert "lowest" in decision.best_reason


def test_not_eligible_reports_most_common_reason():
    decision = decide(make_applicant(credit_score=600), [make_lender("A"), make_lender("B")])
    assert not decision.eligible
    assert decision.not_eligible_reasons[0][:2] == ("credit_score_below_minimum", 2)
    assert "NOT ELIGIBLE" in format_decision(make_applicant(credit_score=600), decision)


def test_emi_and_amount_round_trip():
    amount = amount_for_emi(10000, 12, 24)
    assert emi_for(amount, 12, 24) == pytest.approx(10000)


def test_indian_number_format():
    assert inr(1234567) == "Rs 12,34,567"
    assert inr(500000) == "Rs 5,00,000"
    assert inr(950) == "Rs 950"
