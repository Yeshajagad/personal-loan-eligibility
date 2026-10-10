from dataclasses import fields

import pytest

from src.loan_model.common import DATA_DIR, read_csv
from src.loan_model.models import Applicant

GOOD = dict(
    age_years=29, employment_type="salaried", employer_category="large_private",
    monthly_income_inr=60000, total_experience_months=72, current_job_months=30,
    city="Ahmedabad", credit_score=745, existing_emi_inr=8000,
    loan_amount_requested_inr=500000, tenure_requested_months=36,
)


def test_valid_applicant_is_created():
    assert Applicant(**GOOD).recent_defaults is False


def test_self_employed_employer_category_is_normalised():
    a = Applicant(**{**GOOD, "employment_type": "self_employed"})
    assert a.employer_category == "not_applicable"


def test_no_credit_history_is_allowed():
    assert Applicant(**{**GOOD, "credit_score": None}).credit_score is None


def test_all_errors_are_reported_together():
    with pytest.raises(ValueError) as err:
        Applicant(**{**GOOD, "age_years": 15, "monthly_income_inr": -5})
    assert "age_years" in str(err.value)
    assert "monthly_income_inr" in str(err.value)


def test_credit_score_out_of_range_rejected():
    with pytest.raises(ValueError):
        Applicant(**{**GOOD, "credit_score": 950})


def test_datapoints_csv_matches_applicant_class():
    _, rows = read_csv(DATA_DIR / "datapoints.csv")
    assert {r["name"] for r in rows} == {f.name for f in fields(Applicant)}
