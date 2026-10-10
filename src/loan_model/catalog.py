"""The fixed list of rule names the model understands."""

RULE_CATALOG = {
    "employment_types_allowed":     {"unit": "list",   "description": "Employment types served, joined by | (salaried|self_employed)"},
    "min_age":                      {"unit": "years",  "description": "Minimum applicant age"},
    "max_age_at_maturity":          {"unit": "years",  "description": "Maximum age when the loan ends"},
    "min_monthly_income":           {"unit": "INR",    "description": "Minimum net monthly income"},
    "min_credit_score":             {"unit": "score",  "description": "Minimum bureau score"},
    "min_total_experience_months":  {"unit": "months", "description": "Minimum total work experience"},
    "min_current_job_months":       {"unit": "months", "description": "Minimum time in current job or business"},
    "employer_categories_allowed":  {"unit": "list",   "description": "Accepted employer categories, joined by |"},
    "max_foir_pct":                 {"unit": "percent","description": "Max share of income that total EMIs (old + new) may take"},
    "max_income_multiple":          {"unit": "times",  "description": "Max loan as a multiple of monthly income"},
    "min_loan_amount":              {"unit": "INR",    "description": "Smallest loan offered"},
    "max_loan_amount":              {"unit": "INR",    "description": "Largest loan offered"},
    "min_tenure_months":            {"unit": "months", "description": "Shortest tenure"},
    "max_tenure_months":            {"unit": "months", "description": "Longest tenure"},
    "rate_min_pct":                 {"unit": "percent","description": "Lowest interest rate p.a."},
    "rate_max_pct":                 {"unit": "percent","description": "Highest interest rate p.a."},
    "processing_fee_pct":           {"unit": "percent","description": "Processing fee (information only)"},
}

TEXT_RULES = {"employment_types_allowed", "employer_categories_allowed"}

# The engine cannot evaluate a lender without these.
CORE_RULES = (
    "employment_types_allowed", "min_age", "max_age_at_maturity", "min_monthly_income",
    "min_credit_score", "max_foir_pct", "min_loan_amount", "max_loan_amount",
    "min_tenure_months", "max_tenure_months", "rate_min_pct", "rate_max_pct",
)

APPLIES_TO = {"all", "salaried", "self_employed"}
CITY_GROUPS = {"all", "metro", "other"}
RULE_STATUSES = {"listed", "derived", "estimated"}
