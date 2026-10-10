# Test profile results

Rules file used: `data/lender_rules.csv`  
Profiles: 14

## P01_typical_salaried

_Typical mid-career private salaried applicant, good score_

Input: `{"age_years": 29, "employment_type": "salaried", "employer_category": "large_private", "monthly_income_inr": 60000, "total_experience_months": 72, "current_job_months": 30, "city": "Ahmedabad", "credit_score": 745, "existing_emi_inr": 8000, "loan_amount_requested_inr": 500000, "tenure_requested_months": 36, "recent_defaults": false}`

```
Request: Rs 5,00,000 over 36 months
DECISION: ELIGIBLE - 17 lender(s) would approve
  Canara Bank                  up to Rs 11,47,000   rate ~9.95%  tenure 12-84 months
  HDFC Bank                    up to Rs 6,79,000    rate ~10.24%  tenure 12-72 months
  State Bank of India          up to Rs 9,57,000    rate ~10.25%  tenure 6-84 months
  Punjab National Bank         up to Rs 6,76,000    rate ~10.52%  tenure 12-72 months
  ICICI Bank                   up to Rs 5,82,000    rate ~10.69%  tenure 12-84 months
  IndusInd Bank                up to Rs 5,00,000    rate ~10.74%  tenure 12-48 months
  Bank of Baroda               up to Rs 6,72,000    rate ~10.9%  tenure 12-60 months
  Bajaj Finance                up to Rs 6,71,000    rate ~11.03%  tenure 12-108 months
  Kotak Mahindra Bank          up to Rs 6,68,000    rate ~11.37%  tenure 12-72 months
  Navi                         up to Rs 6,65,000    rate ~11.66%  tenure 12-72 months
  Poonawalla Fincorp           up to Rs 6,60,000    rate ~12.19%  tenure 12-84 months
  Aditya Birla Capital         up to Rs 6,51,000    rate ~13.19%  tenure 12-84 months
  IDFC FIRST Bank              up to Rs 6,48,000    rate ~13.49%  tenure 9-60 months
  Moneyview                    up to Rs 6,33,000    rate ~15.1%  tenure 3-60 months
  Tata Capital                 up to Rs 6,31,000    rate ~15.39%  tenure 12-72 months
  Hero FinCorp                 up to Rs 5,89,000    rate ~20.32%  tenure 12-36 months
  Fibe                         up to Rs 4,35,000    rate ~19.1%  tenure 6-36 months  (below requested amount)
BEST OPTION: Canara Bank
  Why: it can lend the full Rs 5,00,000 requested, and its estimated rate of 9.95% is the lowest (or tied lowest) of 16 comparable lenders (next: HDFC Bank at 10.24%)
```

## P02_high_income_govt

_High income, government employee, excellent score, metro city_

Input: `{"age_years": 38, "employment_type": "salaried", "employer_category": "govt_psu", "monthly_income_inr": 150000, "total_experience_months": 180, "current_job_months": 120, "city": "Mumbai", "credit_score": 810, "existing_emi_inr": 20000, "loan_amount_requested_inr": 2000000, "tenure_requested_months": 60, "recent_defaults": false}`

```
Request: Rs 20,00,000 over 60 months
DECISION: ELIGIBLE - 17 lender(s) would approve
  Canara Bank                  up to Rs 37,50,000   rate ~9.7%  tenure 12-84 months
  Navi                         up to Rs 20,00,000   rate ~9.9%  tenure 12-72 months
  HDFC Bank                    up to Rs 25,89,000   rate ~9.99%  tenure 12-72 months
  Poonawalla Fincorp           up to Rs 25,89,000   rate ~9.99%  tenure 12-84 months
  ICICI Bank                   up to Rs 22,36,000   rate ~9.99%  tenure 12-84 months
  State Bank of India          up to Rs 36,47,000   rate ~10.0%  tenure 6-84 months
  Bajaj Finance                up to Rs 25,88,000   rate ~10.0%  tenure 12-108 months
  Bank of Baroda               up to Rs 20,00,000   rate ~10.15%  tenure 12-60 months
  Punjab National Bank         up to Rs 20,00,000   rate ~10.3%  tenure 12-72 months
  Aditya Birla Capital         up to Rs 25,30,000   rate ~10.99%  tenure 12-84 months
  Kotak Mahindra Bank          up to Rs 25,30,000   rate ~10.99%  tenure 12-72 months
  Tata Capital                 up to Rs 25,30,000   rate ~10.99%  tenure 12-72 months
  IDFC FIRST Bank              up to Rs 15,00,000   rate ~9.99%  tenure 9-60 months  (below requested amount)
  IndusInd Bank                up to Rs 5,00,000    rate ~10.49%  tenure 12-48 months  (below requested amount)
  Moneyview                    up to Rs 10,00,000   rate ~14.0%  tenure 3-60 months  (below requested amount)
  Hero FinCorp                 up to Rs 7,00,000    rate ~17.9%  tenure 12-36 months  (below requested amount)
  Fibe                         up to Rs 10,00,000   rate ~18.0%  tenure 6-36 months  (below requested amount)
BEST OPTION: Canara Bank
  Why: it can lend the full Rs 20,00,000 requested, and its estimated rate of 9.7% is the lowest (or tied lowest) of 12 comparable lenders (next: Navi at 9.9%)
```

## P03_low_score

_Edge case: low credit score (640)_

Input: `{"age_years": 31, "employment_type": "salaried", "employer_category": "other_private", "monthly_income_inr": 45000, "total_experience_months": 84, "current_job_months": 36, "city": "Pune", "credit_score": 640, "existing_emi_inr": 5000, "loan_amount_requested_inr": 300000, "tenure_requested_months": 36, "recent_defaults": false}`

```
Request: Rs 3,00,000 over 36 months
DECISION: NOT ELIGIBLE with any lender checked
Main reasons:
  - Credit score is below the lender's minimum (17 of 20 lenders)
  - Rule data missing for this lender: employment_types_allowed (2 of 20 lenders)
  - Rule data missing for this lender: min_monthly_income (1 of 20 lenders)
```

## P04_high_existing_emi

_Edge case: good score but existing EMIs already take most of the income_

Input: `{"age_years": 35, "employment_type": "salaried", "employer_category": "mnc_listed", "monthly_income_inr": 70000, "total_experience_months": 120, "current_job_months": 60, "city": "Bengaluru", "credit_score": 760, "existing_emi_inr": 45000, "loan_amount_requested_inr": 400000, "tenure_requested_months": 36, "recent_defaults": false}`

```
Request: Rs 4,00,000 over 36 months
DECISION: ELIGIBLE - 1 lender(s) would approve
  Canara Bank                  up to Rs 2,33,000    rate ~9.7%  tenure 12-84 months  (below requested amount)
BEST OPTION: Canara Bank
  Why: no approving lender covers the full Rs 4,00,000; this one offers up to Rs 2,33,000
```

## P05_new_job

_Edge case: only 2 months in the current job_

Input: `{"age_years": 26, "employment_type": "salaried", "employer_category": "large_private", "monthly_income_inr": 55000, "total_experience_months": 48, "current_job_months": 2, "city": "Hyderabad", "credit_score": 730, "existing_emi_inr": 0, "loan_amount_requested_inr": 300000, "tenure_requested_months": 24, "recent_defaults": false}`

```
Request: Rs 3,00,000 over 24 months
DECISION: ELIGIBLE - 10 lender(s) would approve
  IndusInd Bank                up to Rs 5,00,000    rate ~11.49%  tenure 12-48 months
  Kotak Mahindra Bank          up to Rs 5,81,000    rate ~12.53%  tenure 12-72 months
  ICICI Bank                   up to Rs 5,21,000    rate ~12.79%  tenure 12-84 months
  Bajaj Finance                up to Rs 5,72,000    rate ~14.1%  tenure 12-108 months
  Navi                         up to Rs 5,56,000    rate ~16.92%  tenure 12-72 months
  Moneyview                    up to Rs 5,48,000    rate ~18.4%  tenure 3-60 months
  Poonawalla Fincorp           up to Rs 5,46,000    rate ~18.79%  tenure 12-84 months
  Fibe                         up to Rs 4,22,000    rate ~22.4%  tenure 6-36 months
  IDFC FIRST Bank              up to Rs 5,20,000    rate ~23.99%  tenure 9-60 months
  Hero FinCorp                 up to Rs 5,02,000    rate ~27.58%  tenure 12-36 months
BEST OPTION: IndusInd Bank
  Why: it can lend the full Rs 3,00,000 requested, and its estimated rate of 11.49% is the lowest (or tied lowest) of 10 comparable lenders (next: Kotak Mahindra Bank at 12.53%)
```

## P06_fresher_no_credit_history

_Edge case: 4 months of experience and no credit history_

Input: `{"age_years": 22, "employment_type": "salaried", "employer_category": "other_private", "monthly_income_inr": 28000, "total_experience_months": 4, "current_job_months": 4, "city": "Jaipur", "credit_score": null, "existing_emi_inr": 0, "loan_amount_requested_inr": 100000, "tenure_requested_months": 12, "recent_defaults": false}`

```
Request: Rs 1,00,000 over 12 months
DECISION: NOT ELIGIBLE with any lender checked
Main reasons:
  - No credit history (lender needs a bureau score) (17 of 20 lenders)
  - Time in the current job or business is below the lender's minimum (7 of 20 lenders)
  - Total work experience is below the lender's minimum (5 of 20 lenders)
```

## P07_self_employed_established

_Edge case: self-employed with 8 years of business vintage_

Input: `{"age_years": 41, "employment_type": "self_employed", "employer_category": "not_applicable", "monthly_income_inr": 120000, "total_experience_months": 180, "current_job_months": 96, "city": "Surat", "credit_score": 735, "existing_emi_inr": 15000, "loan_amount_requested_inr": 1000000, "tenure_requested_months": 48, "recent_defaults": false}`

```
Request: Rs 10,00,000 over 48 months
DECISION: ELIGIBLE - 10 lender(s) would approve
  HDFC Bank                    up to Rs 17,49,000   rate ~10.74%  tenure 12-72 months
  ICICI Bank                   up to Rs 14,78,000   rate ~12.09%  tenure 12-84 months
  Bank of Baroda               up to Rs 16,96,000   rate ~12.4%  tenure 12-60 months
  Bajaj Finance                up to Rs 16,75,000   rate ~13.07%  tenure 12-108 months
  Navi                         up to Rs 16,12,000   rate ~15.16%  tenure 12-72 months
  Moneyview                    up to Rs 10,00,000   rate ~17.3%  tenure 3-60 months
  Tata Capital                 up to Rs 13,75,000   rate ~24.2%  tenure 12-72 months
  Union Bank of India          up to Rs 5,00,000    rate ~9.88%  tenure 12-60 months  (below requested amount)
  IndusInd Bank                up to Rs 5,00,000    rate ~11.24%  tenure 12-48 months  (below requested amount)
  Hero FinCorp                 up to Rs 7,00,000    rate ~25.16%  tenure 12-36 months  (below requested amount)
BEST OPTION: HDFC Bank
  Why: it can lend the full Rs 10,00,000 requested, and its estimated rate of 10.74% is the lowest (or tied lowest) of 7 comparable lenders (next: ICICI Bank at 12.09%)
```

## P08_self_employed_new_business

_Edge case: self-employed, business only 10 months old_

Input: `{"age_years": 33, "employment_type": "self_employed", "employer_category": "not_applicable", "monthly_income_inr": 80000, "total_experience_months": 60, "current_job_months": 10, "city": "Delhi", "credit_score": 720, "existing_emi_inr": 0, "loan_amount_requested_inr": 500000, "tenure_requested_months": 36, "recent_defaults": false}`

```
Request: Rs 5,00,000 over 36 months
DECISION: ELIGIBLE - 5 lender(s) would approve
  Union Bank of India          up to Rs 5,00,000    rate ~10.41%  tenure 12-60 months
  IndusInd Bank                up to Rs 5,00,000    rate ~11.99%  tenure 12-48 months
  Bajaj Finance                up to Rs 11,35,000   rate ~16.15%  tenure 12-108 months
  Navi                         up to Rs 10,70,000   rate ~20.43%  tenure 12-72 months
  Moneyview                    up to Rs 10,00,000   rate ~20.6%  tenure 3-60 months
BEST OPTION: Union Bank of India
  Why: it can lend the full Rs 5,00,000 requested, and its estimated rate of 10.41% is the lowest (or tied lowest) of 5 comparable lenders (next: IndusInd Bank at 11.99%)
```

## P09_age_near_upper_limit

_Edge case: age 58, so the tenure is capped by maximum age at maturity_

Input: `{"age_years": 58, "employment_type": "salaried", "employer_category": "govt_psu", "monthly_income_inr": 110000, "total_experience_months": 420, "current_job_months": 300, "city": "Chennai", "credit_score": 790, "existing_emi_inr": 10000, "loan_amount_requested_inr": 600000, "tenure_requested_months": 60, "recent_defaults": false}`

```
Request: Rs 6,00,000 over 60 months
DECISION: ELIGIBLE - 12 lender(s) would approve
  Canara Bank                  up to Rs 15,75,000   rate ~9.7%  tenure 12-24 months
  Navi                         up to Rs 9,76,000    rate ~9.9%  tenure 12-24 months
  HDFC Bank                    up to Rs 9,75,000    rate ~9.99%  tenure 12-24 months
  IDFC FIRST Bank              up to Rs 9,75,000    rate ~9.99%  tenure 9-24 months
  Poonawalla Fincorp           up to Rs 9,75,000    rate ~9.99%  tenure 12-24 months
  Bajaj Finance                up to Rs 21,17,000   rate ~10.0%  tenure 12-108 months
  State Bank of India          up to Rs 13,32,000   rate ~10.0%  tenure 6-24 months
  Bank of Baroda               up to Rs 9,73,000    rate ~10.15%  tenure 12-24 months
  Punjab National Bank         up to Rs 9,72,000    rate ~10.3%  tenure 12-24 months
  Aditya Birla Capital         up to Rs 9,65,000    rate ~10.99%  tenure 12-24 months
  Kotak Mahindra Bank          up to Rs 9,65,000    rate ~10.99%  tenure 12-24 months
  IndusInd Bank                up to Rs 5,00,000    rate ~10.49%  tenure 12-24 months  (below requested amount)
BEST OPTION: Canara Bank
  Why: it can lend the full Rs 6,00,000 requested, and its estimated rate of 9.7% is the lowest (or tied lowest) of 11 comparable lenders (next: Navi at 9.9%)
```

## P10_age_at_lower_limit_low_income

_Edge case: age 21 (many lenders' minimum) with low income_

Input: `{"age_years": 21, "employment_type": "salaried", "employer_category": "other_private", "monthly_income_inr": 26000, "total_experience_months": 12, "current_job_months": 12, "city": "Lucknow", "credit_score": 700, "existing_emi_inr": 0, "loan_amount_requested_inr": 150000, "tenure_requested_months": 24, "recent_defaults": false}`

```
Request: Rs 1,50,000 over 24 months
DECISION: ELIGIBLE - 9 lender(s) would approve
  Canara Bank                  up to Rs 4,13,000    rate ~12.2%  tenure 12-84 months
  State Bank of India          up to Rs 3,57,000    rate ~12.5%  tenure 6-84 months
  IndusInd Bank                up to Rs 2,73,000    rate ~12.99%  tenure 12-48 months
  Bajaj Finance                up to Rs 2,54,000    rate ~20.25%  tenure 12-108 months
  Moneyview                    up to Rs 2,43,000    rate ~25.0%  tenure 3-60 months
  Navi                         up to Rs 2,38,000    rate ~27.45%  tenure 12-72 months
  Fibe                         up to Rs 1,87,000    rate ~29.0%  tenure 6-36 months
  Poonawalla Fincorp           up to Rs 2,28,000    rate ~31.99%  tenure 12-84 months
  Aditya Birla Capital         up to Rs 2,26,000    rate ~32.99%  tenure 12-84 months
BEST OPTION: Canara Bank
  Why: it can lend the full Rs 1,50,000 requested, and its estimated rate of 12.2% is the lowest (or tied lowest) of 9 comparable lenders (next: State Bank of India at 12.5%)
```

## P11_recent_default

_Edge case: high score but a recent settlement / 90+ day delay on the report_

Input: `{"age_years": 36, "employment_type": "salaried", "employer_category": "large_private", "monthly_income_inr": 90000, "total_experience_months": 140, "current_job_months": 70, "city": "Kolkata", "credit_score": 770, "existing_emi_inr": 12000, "loan_amount_requested_inr": 500000, "tenure_requested_months": 36, "recent_defaults": true}`

```
Request: Rs 5,00,000 over 36 months
DECISION: NOT ELIGIBLE with any lender checked
Main reasons:
  - Recent default, settlement or 90+ day delay on the credit report (17 of 20 lenders)
  - Rule data missing for this lender: employment_types_allowed (2 of 20 lenders)
  - Rule data missing for this lender: min_monthly_income (1 of 20 lenders)
```

## P12_very_large_loan_request

_Edge case: Rs 50 lakh requested, tests maximum loan amount and income-multiple caps_

Input: `{"age_years": 34, "employment_type": "salaried", "employer_category": "mnc_listed", "monthly_income_inr": 200000, "total_experience_months": 120, "current_job_months": 48, "city": "Gurugram", "credit_score": 800, "existing_emi_inr": 30000, "loan_amount_requested_inr": 5000000, "tenure_requested_months": 84, "recent_defaults": false}`

```
Request: Rs 50,00,000 over 84 months
DECISION: ELIGIBLE - 17 lender(s) would approve
  State Bank of India          up to Rs 50,00,000   rate ~10.0%  tenure 6-84 months
  Canara Bank                  up to Rs 40,00,000   rate ~9.7%  tenure 12-84 months  (below requested amount)
  Navi                         up to Rs 20,00,000   rate ~9.9%  tenure 12-72 months  (below requested amount)
  Poonawalla Fincorp           up to Rs 42,17,000   rate ~9.99%  tenure 12-84 months  (below requested amount)
  HDFC Bank                    up to Rs 37,79,000   rate ~9.99%  tenure 12-72 months  (below requested amount)
  ICICI Bank                   up to Rs 36,15,000   rate ~9.99%  tenure 12-84 months  (below requested amount)
  IDFC FIRST Bank              up to Rs 15,00,000   rate ~9.99%  tenure 9-60 months  (below requested amount)
  Bajaj Finance                up to Rs 42,16,000   rate ~10.0%  tenure 12-108 months  (below requested amount)
  Bank of Baroda               up to Rs 20,00,000   rate ~10.15%  tenure 12-60 months  (below requested amount)
  Punjab National Bank         up to Rs 20,00,000   rate ~10.3%  tenure 12-72 months  (below requested amount)
  IndusInd Bank                up to Rs 5,00,000    rate ~10.49%  tenure 12-48 months  (below requested amount)
  Aditya Birla Capital         up to Rs 40,89,000   rate ~10.99%  tenure 12-84 months  (below requested amount)
  Kotak Mahindra Bank          up to Rs 36,78,000   rate ~10.99%  tenure 12-72 months  (below requested amount)
  Tata Capital                 up to Rs 35,00,000   rate ~10.99%  tenure 12-72 months  (below requested amount)
  Moneyview                    up to Rs 10,00,000   rate ~14.0%  tenure 3-60 months  (below requested amount)
  Hero FinCorp                 up to Rs 7,00,000    rate ~17.9%  tenure 12-36 months  (below requested amount)
  Fibe                         up to Rs 10,00,000   rate ~18.0%  tenure 6-36 months  (below requested amount)
BEST OPTION: State Bank of India
  Why: it can lend the full Rs 50,00,000 requested
```

## P13_borderline_score_650

_Edge case: score exactly 650, a common cut-off_

Input: `{"age_years": 30, "employment_type": "salaried", "employer_category": "large_private", "monthly_income_inr": 50000, "total_experience_months": 72, "current_job_months": 24, "city": "Ahmedabad", "credit_score": 650, "existing_emi_inr": 5000, "loan_amount_requested_inr": 250000, "tenure_requested_months": 36, "recent_defaults": false}`

```
Request: Rs 2,50,000 over 36 months
DECISION: ELIGIBLE - 9 lender(s) would approve
  Canara Bank                  up to Rs 9,41,000    rate ~14.7%  tenure 12-84 months
  Punjab National Bank         up to Rs 5,78,000    rate ~14.75%  tenure 12-72 months
  HDFC Bank                    up to Rs 5,77,000    rate ~14.99%  tenure 12-72 months
  State Bank of India          up to Rs 7,93,000    rate ~15.0%  tenure 6-84 months
  IndusInd Bank                up to Rs 5,00,000    rate ~15.49%  tenure 12-48 months
  Bajaj Finance                up to Rs 4,68,000    rate ~30.5%  tenure 12-108 months
  Moneyview                    up to Rs 4,36,000    rate ~36.0%  tenure 3-60 months
  Fibe                         up to Rs 3,11,000    rate ~40.0%  tenure 6-36 months
  Navi                         up to Rs 3,91,000    rate ~45.0%  tenure 12-72 months
BEST OPTION: Canara Bank
  Why: it can lend the full Rs 2,50,000 requested, and its estimated rate of 14.7% is the lowest (or tied lowest) of 9 comparable lenders (next: Punjab National Bank at 14.75%)
```

## P14_income_below_most_floors

_Edge case: Rs 18,000 monthly income in a non-metro city_

Input: `{"age_years": 27, "employment_type": "salaried", "employer_category": "other_private", "monthly_income_inr": 18000, "total_experience_months": 30, "current_job_months": 18, "city": "Rajkot", "credit_score": 710, "existing_emi_inr": 0, "loan_amount_requested_inr": 80000, "tenure_requested_months": 18, "recent_defaults": false}`

```
Request: Rs 80,000 over 18 months
DECISION: ELIGIBLE - 1 lender(s) would approve
  IDFC FIRST Bank              up to Rs 1,22,000    rate ~38.0%  tenure 9-60 months
BEST OPTION: IDFC FIRST Bank
  Why: it can lend the full Rs 80,000 requested
```
