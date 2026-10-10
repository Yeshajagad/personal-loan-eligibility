import json

from src.loan_model.common import DATA_DIR
from src.loan_model.engine import decide
from src.loan_model.models import Applicant
from src.loan_model.rules import load_all


def test_real_rules_load_and_every_profile_runs():
    lenders = load_all()
    assert len(lenders) >= 18
    with open(DATA_DIR / "test_profiles.json", encoding="utf-8") as f:
        cases = json.load(f)
    for case in cases:
        decide(Applicant(**case["profile"]), lenders)  # must not raise
