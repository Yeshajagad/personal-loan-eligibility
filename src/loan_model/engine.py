"""The rule engine: which lenders approve this applicant, and which is best."""
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from .catalog import CORE_RULES
from .models import Applicant
from .rules import LenderRules

# Assumption: our own metro list. Lenders may use different lists.
METRO_CITIES = {
    "mumbai", "delhi", "new delhi", "gurgaon", "gurugram", "noida", "bengaluru",
    "bangalore", "chennai", "hyderabad", "kolkata", "pune",
}
BEST_RATE_SCORE = 750  # assumption: scores at or above this get the lender's lowest rate

REASON_MESSAGES = {
    "employment_type_not_served": "Lender does not serve this employment type",
    "below_min_age": "Applicant is younger than the lender's minimum age",
    "age_too_high_for_minimum_tenure": "Applicant is too close to the lender's maximum age at loan maturity",
    "income_below_minimum": "Monthly income is below the lender's minimum",
    "no_credit_history": "No credit history (lender needs a bureau score)",
    "credit_score_below_minimum": "Credit score is below the lender's minimum",
    "recent_default_or_delinquency": "Recent default, settlement or 90+ day delay on the credit report",
    "total_experience_too_low": "Total work experience is below the lender's minimum",
    "current_job_too_short": "Time in the current job or business is below the lender's minimum",
    "employer_category_not_accepted": "Employer category is not accepted by the lender",
    "foir_exceeded": "Existing EMIs already use the share of income the lender allows (FOIR)",
    "loan_capacity_below_lender_minimum": "Affordable loan amount is below the lender's minimum loan",
}


def reason_text(code):
    if code.startswith("missing_rule:"):
        return "Rule data missing for this lender: " + code.split(":", 1)[1]
    return REASON_MESSAGES.get(code, code)


@dataclass
class LenderResult:
    lender_id: str
    lender_name: str
    approved: bool = False
    reasons: list = field(default_factory=list)
    max_amount: float = 0.0
    rate_pct: Optional[float] = None
    tenure_min_months: Optional[int] = None
    tenure_max_months: Optional[int] = None
    tenure_used_months: Optional[int] = None
    emi_at_max_amount: Optional[float] = None
    covers_request: bool = False


@dataclass
class Decision:
    eligible: bool
    approvals: list
    rejections: list
    best: Optional[LenderResult]
    best_reason: str
    not_eligible_reasons: list  # (reason_code, lenders_hit, total_lenders)


# ---------- maths ----------

def emi_for(amount, annual_rate_pct, months):
    r = annual_rate_pct / 1200
    if r == 0:
        return amount / months
    return amount * r / (1 - (1 + r) ** -months)


def amount_for_emi(emi, annual_rate_pct, months):
    r = annual_rate_pct / 1200
    if r == 0:
        return emi * months
    return emi * (1 - (1 + r) ** -months) / r


def estimate_rate(rate_min, rate_max, score, min_score):
    """Estimate: best rate at 750+, worst rate at the lender's minimum score."""
    spread = max(BEST_RATE_SCORE - min_score, 1)
    position = min(max((BEST_RATE_SCORE - score) / spread, 0.0), 1.0)
    return round(rate_min + (rate_max - rate_min) * position, 2)


def city_group(city):
    return "metro" if city.strip().lower() in METRO_CITIES else "other"


def inr(amount):
    """Format with Indian digit grouping, e.g. Rs 12,34,567."""
    digits = str(int(round(amount)))
    if len(digits) <= 3:
        return "Rs " + digits
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return "Rs " + ",".join(groups + [tail])


# ---------- one lender ----------

def evaluate_lender(applicant: Applicant, lender: LenderRules) -> LenderResult:
    result = LenderResult(lender.lender_id, lender.name)
    emp = applicant.employment_type
    group = city_group(applicant.city)

    def get(rule_name):
        return lender.value(rule_name, emp, group)

    allowed = get("employment_types_allowed")
    if allowed is None:
        result.reasons.append("missing_rule:employment_types_allowed")
        return result
    if emp not in allowed:
        result.reasons.append("employment_type_not_served")
        return result

    missing = [name for name in CORE_RULES if get(name) is None]
    if missing:
        result.reasons.extend(f"missing_rule:{name}" for name in missing)
        return result

    reasons = result.reasons
    if applicant.age_years < get("min_age"):
        reasons.append("below_min_age")
    if applicant.monthly_income_inr < get("min_monthly_income"):
        reasons.append("income_below_minimum")

    min_score = get("min_credit_score")
    if applicant.credit_score is None:
        reasons.append("no_credit_history")
    elif applicant.credit_score < min_score:
        reasons.append("credit_score_below_minimum")
    if applicant.recent_defaults:
        reasons.append("recent_default_or_delinquency")

    min_total = get("min_total_experience_months")
    if min_total is not None and applicant.total_experience_months < min_total:
        reasons.append("total_experience_too_low")
    min_current = get("min_current_job_months")
    if min_current is not None and applicant.current_job_months < min_current:
        reasons.append("current_job_too_short")
    if emp == "salaried":
        categories = get("employer_categories_allowed")
        if categories and applicant.employer_category not in categories:
            reasons.append("employer_category_not_accepted")

    # Loan must finish before the maximum age at maturity.
    months_to_max_age = int((get("max_age_at_maturity") - applicant.age_years) * 12)
    tenure_min = int(get("min_tenure_months"))
    tenure_max = min(int(get("max_tenure_months")), months_to_max_age)
    tenure_ok = tenure_max >= tenure_min
    if not tenure_ok:
        reasons.append("age_too_high_for_minimum_tenure")

    max_amount = rate = tenure_used = None
    if tenure_ok and applicant.credit_score is not None:
        tenure_used = max(tenure_min, min(applicant.tenure_requested_months, tenure_max))
        rate = estimate_rate(get("rate_min_pct"), get("rate_max_pct"),
                             applicant.credit_score, min_score)
        available_emi = (get("max_foir_pct") / 100) * applicant.monthly_income_inr \
            - applicant.existing_emi_inr
        if available_emi <= 0:
            reasons.append("foir_exceeded")
        else:
            caps = [amount_for_emi(available_emi, rate, tenure_used), get("max_loan_amount")]
            multiple = get("max_income_multiple")
            if multiple is not None:
                caps.append(multiple * applicant.monthly_income_inr)
            max_amount = math.floor(min(caps) / 1000) * 1000
            if max_amount < get("min_loan_amount"):
                reasons.append("loan_capacity_below_lender_minimum")

    if reasons:
        return result  # rejected: approved stays False, max_amount stays 0

    result.approved = True
    result.max_amount = max_amount
    result.rate_pct = rate
    result.tenure_min_months = tenure_min
    result.tenure_max_months = tenure_max
    result.tenure_used_months = tenure_used
    result.emi_at_max_amount = round(emi_for(max_amount, rate, tenure_used), 2)
    result.covers_request = max_amount >= applicant.loan_amount_requested_inr
    return result


# ---------- all lenders ----------

def explain_best(best, approvals, requested):
    if best.covers_request:
        text = f"it can lend the full {inr(requested)} requested"
    else:
        text = (f"no approving lender covers the full {inr(requested)}; "
                f"this one offers up to {inr(best.max_amount)}")
    pool = [r for r in approvals if r.covers_request == best.covers_request]
    if len(pool) > 1:
        text += (f", and its estimated rate of {best.rate_pct}% is the lowest (or tied lowest) "
                 f"of {len(pool)} comparable lenders (next: {pool[1].lender_name} at {pool[1].rate_pct}%)")
    return text


def decide(applicant: Applicant, lenders: list) -> Decision:
    results = [evaluate_lender(applicant, lender) for lender in lenders]
    approvals = [r for r in results if r.approved]
    rejections = [r for r in results if not r.approved]
    approvals.sort(key=lambda r: (not r.covers_request, r.rate_pct, -r.max_amount, r.lender_id))

    if approvals:
        best = approvals[0]
        return Decision(True, approvals, rejections, best,
                        explain_best(best, approvals, applicant.loan_amount_requested_inr), [])

    counts = Counter(code for r in rejections for code in set(r.reasons))
    total = len(rejections)
    common = [(code, n, total) for code, n in counts.most_common() if n == total]
    top = common or [(code, n, total) for code, n in counts.most_common(3)]
    return Decision(False, [], rejections, None, "", top)


def format_decision(applicant: Applicant, decision: Decision) -> str:
    lines = [f"Request: {inr(applicant.loan_amount_requested_inr)} "
             f"over {applicant.tenure_requested_months} months"]
    if not decision.eligible:
        lines.append("DECISION: NOT ELIGIBLE with any lender checked")
        lines.append("Main reasons:")
        for code, count, total in decision.not_eligible_reasons:
            lines.append(f"  - {reason_text(code)} ({count} of {total} lenders)")
        return "\n".join(lines)

    lines.append(f"DECISION: ELIGIBLE - {len(decision.approvals)} lender(s) would approve")
    for r in decision.approvals:
        note = "" if r.covers_request else "  (below requested amount)"
        lines.append(f"  {r.lender_name:<28} up to {inr(r.max_amount):<14} "
                     f"rate ~{r.rate_pct}%  tenure {r.tenure_min_months}-{r.tenure_max_months} months{note}")
    lines.append(f"BEST OPTION: {decision.best.lender_name}")
    lines.append(f"  Why: {decision.best_reason}")
    return "\n".join(lines)
