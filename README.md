# Personal Loan Eligibility: a rule-based model for 20 Indian lenders

Question this project tries to answer: **"Can I get a personal loan, and from whom?"**

Given a person's details (age, job type, income, credit score, existing EMIs, loan wanted), the program says whether they are eligible, which lenders would approve with the maximum amount, rate and tenure, and which one looks best and why. It is rule-based. There is no ML model.

## What is in this repo

| Path | What it is |
|---|---|
| `data/datapoints.csv` | The 12 input variables, with unit, type, allowed values |
| `data/lenders.csv` | The 20 lenders, with product link, why I picked them, source and date read |
| `data/rules_from_sources.csv` | 214 rules exactly as read from lender pages (each with source link, date, note) |
| `data/gap_filling_values.csv` | The fallback values used where a lender does not publish a rule |
| `data/lender_rules.csv` | Final rule table the model uses (267 rows) |
| `data/test_profiles.json` | 14 test profiles |
| `data/link_check_log.csv` | Result of checking every lender link |
| `src/loan_model/` | Code: input checks, rule loading, engine, CLI, test runner, gap filler |
| `tests/` | 24 automated tests |
| `outputs/` | Results for the 14 profiles and rejection statistics |

## How to run

Python 3.9 or newer.

```bash
pip install -r requirements.txt
python -m pytest                                        # 24 tests
python -m src.loan_model.validate_lenders               # checks lenders.csv
python -m src.loan_model.fill_gaps                      # rebuilds data/lender_rules.csv
python -m src.loan_model.validate_rules                 # checks the rule table
python -m src.loan_model.cli data/sample_profile.json   # one applicant
python -m src.loan_model.run_profiles                   # all 14 profiles -> outputs/
```

## 1. How I chose the 20 lenders

There is no official "top 20 personal loan lenders" list, so I used four rules: the lender sells unsecured personal loans, it has a large retail business, the list mixes banks, NBFCs and fintech apps, and its rules can be found publicly.

The result is 12 banks, 5 NBFCs and 3 fintechs (SBI, HDFC, ICICI, Axis, Kotak, IndusInd, Yes Bank, IDFC FIRST, Bank of Baroda, PNB, Canara, Union Bank; Bajaj Finance, Tata Capital, Aditya Birla Capital, Poonawalla Fincorp, Hero FinCorp; Navi, Moneyview, Fibe). Each row in `lenders.csv` has a reason, a source link and the date I read it.

Weak point: for SBI, HDFC, Hero FinCorp, Navi, Moneyview and Fibe the "selection source" is only the lender's own product page. It shows the product exists but does not prove the lender is large. This is a judgement-based list, not a ranking.

I also checked all links on 2026-10-10 (`link_check_log.csv`). The Yes Bank and Navi product pages only load with JavaScript, so I could not read them and their links are marked unverified.

## 2. Input variables

12 variables, listed in `data/datapoints.csv`: age, employment type (salaried / self-employed), employer category, monthly income, total experience, months in current job, city, credit score (can be empty for "no history"), existing EMIs, loan amount wanted, tenure wanted, and recent default flag. The `Applicant` class rejects bad input (negative income, age under 18, and so on) and reports all errors at once.

## 3. How I found the rules

For each lender I read the product page, then the eligibility/FAQ page, then calculators, rate cards and fee tables, and wrote **one row per rule** in `rules_from_sources.csv`: value, unit, who it applies to (all / salaried / self-employed), city group, source link, date read, and a note. All pages were read on 2026-10-10.

Every row carries a status:
- **listed**: the lender's page says it (186 rows)
- **derived**: I calculated it from published numbers, with the working in the note (6 rows)
- **estimated**: indirect evidence, reasoning in the note (75 rows: 22 from the page-reading step and 53 added by the gap filler)

**Unlisted rules.** Lenders do not publish everything the model needs. No lender I found publishes FOIR (the share of income that can go to EMIs). SBI and Bank of Baroda state EMI-to-income limits for some cases, and Union Bank publishes score-linked rate bands, but most lenders publish nothing like this. Rather than type in guesses by hand, `fill_gaps.py` fills each missing rule with a value **computed from the published rows of the other lenders**:

| Rule | Fallback used | How it is computed |
|---|---|---|
| FOIR | 50% | median of the 7 FOIR values found |
| Minimum income | Rs 25,000 | median of 13 published values |
| Minimum credit score | 650 | lowest of 9 published values |
| Minimum age | 21 | most common of 16 values |
| Max age at maturity | 60 | most common of 7 values |
| Min / max tenure | 12 / 72 months | most common / median |
| Minimum loan | Rs 50,000 | median of 11 values |
| Maximum rate | starting rate + 5 points (banks) or + 22 points (non-banks) | median gap between lowest and highest published rate |

A lender is only filled in if its pages gave at least a **maximum loan amount and a starting rate**. Otherwise the model would be inventing the lender. **Axis Bank and Yes Bank did not meet this**, so they are marked "rule data missing" and are not used in any decision. Union Bank's salaried scheme also has no loan cap found, so it is skipped for salaried applicants; its self-employed rules are used.

## 4. How the model decides

1. **Hard checks** per lender: employment type served, age, minimum income, credit score, recent default, experience and time in current job, employer type. All failing reasons are collected, not just the first.
2. **Tenure** cannot run past the lender's maximum age at maturity.
3. **Rate**: the lender's lowest rate for score 750 and above, the highest rate at the lender's minimum score, and a straight line in between. This is my estimate; lenders do not publish this mapping (except Union Bank's bands, which the code does not use).
4. **EMI room** = FOIR x income - existing EMIs. Zero or less means rejection.
5. **Maximum loan** = loan that the EMI room can repay over the tenure, `EMI x (1 - (1+r)^-n) / r`, capped by the lender's maximum and any income-multiple rule, rounded down to Rs 1,000.
6. A person is eligible if at least one lender approves.
7. **Best option**: lenders that cover the requested amount come first, then the lowest rate, then the highest amount. The explanation is printed with the result.
8. If a core rule is missing for a lender, the answer for that lender is "rule data missing", never a guess.

Metro cities (for city-based income rules): Mumbai, Delhi, Gurugram, Noida, Bengaluru, Chennai, Hyderabad, Kolkata, Pune. This list is my assumption.

## 5. Test profiles and results

14 profiles in `data/test_profiles.json`; full output in `outputs/profile_results.md`.

| ID | What it tests | Result | Best option |
|---|---|---|---|
| P01 | Typical mid-career private salaried applicant, good score | Eligible, 17 lender(s) | Canara Bank |
| P02 | High income, government employee, excellent score, metro city | Eligible, 17 lender(s) | Canara Bank |
| P03 | low credit score (640) | Not eligible | - |
| P04 | good score but existing EMIs already take most of the income | Eligible, 1 lender(s) | Canara Bank |
| P05 | only 2 months in the current job | Eligible, 10 lender(s) | IndusInd Bank |
| P06 | 4 months of experience and no credit history | Not eligible | - |
| P07 | self-employed with 8 years of business vintage | Eligible, 10 lender(s) | HDFC Bank |
| P08 | self-employed, business only 10 months old | Eligible, 5 lender(s) | Union Bank of India |
| P09 | age 58, so the tenure is capped by maximum age at maturity | Eligible, 12 lender(s) | Canara Bank |
| P10 | age 21 (many lenders' minimum) with low income | Eligible, 9 lender(s) | Canara Bank |
| P11 | high score but a recent settlement / 90+ day delay on the report | Not eligible | - |
| P12 | Rs 50 lakh requested, tests maximum loan amount and income-multiple caps | Eligible, 17 lender(s) | State Bank of India |
| P13 | score exactly 650, a common cut-off | Eligible, 9 lender(s) | Canara Bank |
| P14 | Rs 18,000 monthly income in a non-metro city | Eligible, 1 lender(s) | IDFC FIRST Bank |

Counts depend on the 18 lenders with usable rules (Axis and Yes excluded).

## 6. What I noticed

- **Credit score is the rule that rejects most often** (37 of the lender-profile pairs in `outputs/rejection_stats.md`), followed by time in current job (20) and minimum income (19).
- **Banks and NBFCs/fintechs are far apart on price.** Bank rates in the data are roughly 9.3% to 17.5%; NBFC and fintech ranges go up to 30-45%. So the "best option" is almost always a bank for good profiles.
- **Weaker profiles lose most options.** The applicant with heavy existing EMIs (P04) and the applicant with Rs 18,000 income (P14) each had only one approving lender.
- **Lender pages contradict themselves.** ICICI shows age 18-58 and 20-58; IDFC FIRST shows score 710 and 760+; Tata Capital shows a minimum loan of Rs 40,000 and Rs 75,000; Aditya Birla shows a maximum of Rs 50 lakh and Rs 65 lakh; Hero FinCorp shows tenure 12-36 and 6-24 months. In each case I used one value and wrote the conflict in the note.
- **Union Bank is the only lender found with a credit-score-to-rate table** (9.30% for 800+ down to 12.60% below 650). It prices applicants below 650, while my fallback minimum score is 650.

## 7. Limitations

- **Many rules are estimates**: 75 of 267 rows. FOIR is estimated for nearly every lender, so the loan amounts are only as good as that estimate.
- **Axis Bank and Yes Bank have no usable rules** and are not part of the results. Yes Bank and Navi pages could not be read directly.
- The pages were read with a page-reading tool that summarises content, so individual values can be wrong. Rules need to be rechecked against the source link before relying on them.
- Lender rules change. Everything reflects pages as read on 2026-10-10.
- The score-to-rate line is a simplification. Real pricing also depends on income, employer, and relationship with the lender.
- The sample of lenders is mostly private banks and NBFCs; public-sector banks often use salary multiples and salary-account rules that the engine only partly covers.
- This tells someone whether they are *likely* eligible. Final approval is always the lender's decision.

## 8. Next steps

- Open the Axis and Yes Bank pages in a browser and add their rules.
- Recheck every `estimated` row and replace it with a listed or derived value where I can find one.
- Replace the six weak lender-selection sources.
- Add per-lender employer lists and salary-multiple rules for public-sector banks.
- Show a confidence level beside each decision based on how many of the rules used were estimates.
- Compare the model's output with real approval outcomes if such data becomes available.

## Tools

Python (standard library only; `pytest` for tests).