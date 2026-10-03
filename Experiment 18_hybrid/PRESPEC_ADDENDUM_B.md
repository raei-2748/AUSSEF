# Experiment 18, addendum B: check the input-output model only against what it predicts

Written 3 Oct 2026, before any v2 number is computed. Hash in LOCK_B.txt. v1 files are kept unchanged as the record
(their sha256 list is in LOCK_B.txt). New outputs are prefixed `v2_`.

## Why (stated honestly: written after seeing v1)
v1 compared the IO model with five measured limits and concluded the default model "overstates". Re-reading the
comparison (Ray's question, 3 Oct) shows that three of the five limits measure something the IO model does not predict:
- **M3, accommodation and food business counts (CABEE).** A count of registered businesses is a stock. The IO model
  predicts lost sales (a flow). A business that loses months of sales is still counted. So M3 cannot test the model.
- **M1 and M1b, unemployment rate.** The IO model turns lost sales into "job-equivalents" with a fixed jobs-per-dollar
  ratio. Firms usually keep staff through a temporary fall in sales, and from March 2020 JobKeeper held workers on
  payrolls. M1b also fails its placebo (Exp 13). So unemployment cannot test the model's sales loss.
- **M2 and M2b, total income, years 1-2** are what the model does predict (its labour-income change, including income
  earned from rebuild work). These are the valid checks.
The v1 grid (pilot/GRID_B.csv) already shows the default setting inside both income limits (slope -0.95). This addendum
is therefore a correction made after seeing results, and is reported as such (DEVIATIONS D23-D26).

## Changes
1. **Checks.** Primary: M2 (ATO postcode total income, Black Summer, CI -3.1 to +0.8) and M2b (ABS PIA SA2 total
   income, Black Summer, CI -2.6 to -0.7), same slope definition as v1. A setting is **income-consistent** if its slope is
   inside both. Sensitivity: inside M2 only (M2 passes its placebo; M2b has no usable placebo). M1, M1b and M3 are
   reported for the default setting only, as descriptive, with the reasons above. Out-of-sample: share of
   income-consistent settings that are also inside the pre-COVID income limit (M2 P, CI -2.7 to +4.4).
2. **Model fix (v1 audit, minor issue a).** Industries with zero employment in ABS table 20 (owner-occupied dwellings,
   i.e. imputed rent) are removed from the business-interruption shock and from the division output-per-job and
   labour-per-job ratios. Everything else in `src/io_model.py` is unchanged.
3. **Headline quantity: gross lost trade.** Black Summer (season 2019) modelled gross output loss in the first 24 months,
   no rebuild offset, nominal mixed-year A$. Reason: rebuild spending is paid for by insurers and governments, which
   the who-pays account (Exp 17) already counts. The offset is reported separately. Also reported: gross labour-income
   loss and year-1 job-equivalents.
4. **Grid and default unchanged:** the same 1,620 settings (disruption 1-30 months, reach, rebuild share, FLQ delta,
   Type I/II) and the same default (6 months, residents within 1 km, 0.66, 0.3, Type II).
5. **Not re-run:** the hybrid index. Modelled IL is built from fire-size inputs that are also X variables, so it is not
   used in the prediction target Y. v1's Y_hybrid result stays on record as a negative.

## Outputs (results/)
- `v2_IL_GRID.csv`: every setting, its income slope and verdicts, and its Black Summer totals.
- `v2_IL_SUMMARY.json`: n income-consistent settings; Black Summer gross lost trade over those settings (min, 5th
  percentile, median, 95th percentile, max) and the default value; the disruption lengths allowed; the M2-only
  sensitivity; descriptive M1, M1b and M3 slopes for the default; the out-of-sample share.
- `figures/fig5_lost_trade_fair_check.png`.

## How it will be described
"A standard input-output model, checked against measured income in the burned areas, puts Black Summer's lost trade
(not counted in any payer's bill) at A$X to A$Y in the first two years (modelled)." Never "first"; never "no effect".
If no setting is income-consistent, that is reported instead.
