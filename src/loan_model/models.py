"""The Applicant: every input the model needs, with validation."""
from dataclasses import dataclass
from typing import Optional

EMPLOYMENT_TYPES = ("salaried", "self_employed")
EMPLOYER_CATEGORIES = ("govt_psu", "mnc_listed", "large_private", "other_private", "not_applicable")


@dataclass
class Applicant:
    age_years: int
    employment_type: str
    employer_category: str
    monthly_income_inr: float
    total_experience_months: int
    current_job_months: int
    city: str
    credit_score: Optional[int]  # None = no credit history
    existing_emi_inr: float
    loan_amount_requested_inr: float
    tenure_requested_months: int
    recent_defaults: bool = False

    def __post_init__(self):
        self.city = self.city.strip()
        if self.employment_type == "self_employed":
            self.employer_category = "not_applicable"
        self.validate()

    def validate(self):
        """Collect every problem and raise one ValueError listing all of them."""
        errors = []
        if not 18 <= self.age_years <= 100:
            errors.append("age_years must be between 18 and 100")
        if self.employment_type not in EMPLOYMENT_TYPES:
            errors.append(f"employment_type must be one of {EMPLOYMENT_TYPES}")
        if self.employer_category not in EMPLOYER_CATEGORIES:
            errors.append(f"employer_category must be one of {EMPLOYER_CATEGORIES}")
        if self.employment_type == "salaried" and self.employer_category == "not_applicable":
            errors.append("salaried applicants need a real employer_category")
        if self.monthly_income_inr <= 0:
            errors.append("monthly_income_inr must be greater than 0")
        if self.total_experience_months < 0:
            errors.append("total_experience_months cannot be negative")
        if not 0 <= self.current_job_months <= self.total_experience_months:
            errors.append("current_job_months must be between 0 and total_experience_months")
        if not self.city:
            errors.append("city cannot be empty")
        if self.credit_score is not None and not 300 <= self.credit_score <= 900:
            errors.append("credit_score must be 300-900, or None for no credit history")
        if self.existing_emi_inr < 0:
            errors.append("existing_emi_inr cannot be negative")
        if self.loan_amount_requested_inr <= 0:
            errors.append("loan_amount_requested_inr must be greater than 0")
        if self.tenure_requested_months <= 0:
            errors.append("tenure_requested_months must be greater than 0")
        if errors:
            raise ValueError("; ".join(errors))
