import json

from src.loan_model.common import DATA_DIR
from src.loan_model.models import Applicant


def test_there_are_at_least_ten_valid_profiles_with_unique_ids():
    with open(DATA_DIR / "test_profiles.json", encoding="utf-8") as f:
        cases = json.load(f)
    assert len(cases) >= 10
    assert len({c["id"] for c in cases}) == len(cases)
    for case in cases:
        Applicant(**case["profile"])  # raises ValueError if a profile is invalid
