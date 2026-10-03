# Experiment 17: cost accounts (who carried the cost of each fire)

Run order (needs the master workbook and Experiments 6, 7, 10 files):
1. `python3 council_side.py`  -> results/COUNCIL_SIDE.csv (council grants and capital spending after each fire)
2. `python3 summarise.py`     -> runs build_accounts.py, writes results/ACCOUNT_BY_COUNCIL.csv, ACCOUNT_BY_FIRE.csv,
   SUMMARY_BY_FIRE.csv, BLACK_SUMMER_BY_COUNCIL.csv, CHECKS.txt

Inputs: `ASSUMPTIONS.csv` (every assumption, low/mid/high, with bibliography ids). `biblog.py` appends to
`bibliography/parts/exp17_cost_accounts_2026-10-02.csv`. Research agents logged to
`bibliography/parts/exp17_research_{rebuild_cost,insurance_gap,gov_payments}_2026-10-02.csv`.
Results and reading: `FINDINGS.md`. Independent audit: `audit/AUDIT.md`.
Column prefixes in ACCOUNT_BY_COUNCIL.csv: A1 homes, A2 other insured, A3 clean-up, B1 household payments,
B2 programs, memo_ = shown but not added to totals. Suffix _low/_mid/_high = scenario.
