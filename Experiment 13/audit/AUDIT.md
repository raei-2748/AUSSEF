# Experiment 13 - independent audit

Date: 2 Oct 2026. Auditor: fresh reviewer agent (PRESPEC section 7).
All audit code is in this folder and was written from scratch (it does not import or copy `e13lib.py`,
`run_channels.py` or `summarise.py`; those were read only AFTER the numbers below were re-derived, to explain
differences). Model fitting uses pyfixest, but the panels, dose lags, sample rules, placebo design, averaging of
lags, t(G-1) intervals and % conversion are the audit's own code. The ATO income result (A) was also re-fitted with
a fully separate numpy estimator (own fixed-effect removal and own SA3-clustered errors) as a check on pyfixest.

Scripts: `a1_exposure.py` (check 1), `a_ato_parse.py` (ATO raw files), `a_income.py` (A, B),
`a_income_numpy.py` (A without pyfixest), `a_dv_build.py` + `a_dv.py` (C), `a_pia.py` (D), `a_unemp.py` (E),
`alib.py` (shared audit helpers), plus post-hoc checks `a_dv_lostnames.py`, `a_dv_sens.py`, `a_unemp_cover.py`.

## 1. Lock check
- `PRESPEC.md`, `e13lib.py`, `income_ato/build_ato.py`, `exposure/build_exposure.py`: SHA-256 equals `LOCK.txt`.
  The pre-specification was not changed after the lock.
- `run_channels.py`: hash differs from the lock. `deviations/CODE_FIXES.txt` (C1) says one line was changed
  (`p.ne` -> `p['ne']` in the business code). The audit reversed exactly that line
  (`p['ne'] / p['total'].where(p['total'] > 0)` -> `p.ne / p.total.where(p.total > 0)`) and got the locked hash
  `61fa0f08...` back. So that was the only change, and it only touches the business channel.
- `summarise.py` (verdicts, Holm, COVID rule) was written after the lock and is not hashed. Its rules match
  PRESPEC 2.3 and 5 (checked line by line).

## 2. Results table

Effects are per 10 percentage points of H (homes inside the fire outline), average of lag 1 and lag 2,
area FE + SA4 x year FE, SE clustered by SA3, 95% CI from t(G-1) (G = 90 SA3s; 88 for unemployment P).

| Quantity | Main analysis | Audit re-derivation | Match |
|---|---|---|---|
| Check 1: postcode H, fy2013 (max abs difference vs `dose_poa`) | - | 0 (exactly equal) | yes |
| Check 1: postcode H, fy2019 (max abs difference vs `dose_poa`) | - | 0 (exactly equal); 65 postcodes >= 1%, 16 >= 10% as in PRESPEC 0 | yes |
| Check 1: SA3/SA4 = region with most dwellings, 20 random postcodes (and all 624) | - | 0 mismatches | yes |
| ATO raw-file parse (13 years, NSW postcodes): individuals and taxable income vs `panel_ato.parquet` | - | 8,215 postcode-years, 0 difference | yes |
| A. ATO log taxable income, sample B (593 postcodes, 5,337 obs) | -1.18% [-3.10, +0.78] | -1.18% [-3.10, +0.78] (numpy estimator: same estimate, CI [-3.10, +0.78] with the same small-sample factor) | yes |
| A. placebo (fake fire 24 months early), B | +0.98% [-0.41, +2.40] | +0.98% [-0.41, +2.40] (2,965 obs) | yes |
| B. ATO log taxable income, sample P (595 postcodes, 5,355 obs) | +0.79% [-2.69, +4.40] | +0.79% [-2.69, +4.40] | yes |
| B. placebo, P (4,857 obs after dropping post-fire area-years) | +0.92% [-1.65, +3.56] | +0.92% [-1.65, +3.56] | yes |
| C. BOCSAR DV-related assault, suburbs, sample B (2,643 suburbs; 28,380 obs used) | -0.46% [-3.24, +2.41] | -0.46% [-3.24, +2.41] | yes |
| C. placebo, B | +1.99% [-1.48, +5.59] | +1.99% [-1.48, +5.59] | yes |
| C. (extra) DV, sample P | -2.30% [-11.23, +7.52]; placebo -4.84% [-12.61, +3.63] | same | yes |
| D. ABS PIA SA2 log total income, sample B (637 SA2s, 3,809 obs) | -1.65% [-2.60, -0.68] | -1.65% [-2.60, -0.68] | yes |
| D. placebo, B | +0.74% [-0.87, +2.38] | **not estimable** (see issue 1). The +0.74% is the fake lag-0 coefficient alone | **no** |
| E. SALM unemployment rate, sample B (623 SA2s, 5,440 obs), points per 10 pp | -0.087 [-0.29, +0.12] | -0.087 [-0.294, +0.119] | yes |
| E. placebo, B | -0.195 [-0.36, -0.03] (fails) | -0.195 [-0.361, -0.029] (fails) | yes |
| E. (extra) unemployment, sample P | +0.11 [-0.83, +1.05]; placebo +0.53 [-0.30, +1.36] | same | yes |
| Holm over the 10 primary tests | all adjusted p = 1.0 | smallest raw p = 0.146, x10 > 1, so all 1.0 | yes |

Dose timing was checked directly: the financial year is labelled by its starting year in every source (ATO
"2019-20" = 2019, BOCSAR months Jul-Jun, SALM Sep+Dec quarters of year y with Mar+Jun quarters of y+1, PIA
"2019-20" = 2019). Black Summer = fire year 2019 (Jul 2019 - Jun 2020), so lag 1 = 2020-21 and lag 2 = 2021-22,
as the PRESPEC says. In sample P every dose lag uses fire years <= 2018. In sample B, other fire years use lags 0-3
and fire year 2019 is left out of the controls. The placebo uses fake dose[a, t] = real dose[a, t+2] with lags 0 and 1.
B keeps outcome years <= 2018-19 with other fires as controls. P drops every area-year 0-3 years after a fire year with
H >= 0.001 and uses only fires up to 2018-19. All of this matches PRESPEC 2.1-2.2 and the main code.

## 3. Issues found

1. **PIA placebo cannot be estimated, but a number was reported for it (changes a number; does not change a
   verdict as things stand).** The PIA panel starts in 2017-18, so the sample B placebo has only two outcome years
   (2017-18 and 2018-19). Fake lag 0 is H in 2017-18 and fake lag 1 is H in 2018-19, so their sum equals H in both
   years. The area fixed effect absorbs that sum, so the average of the two fake lags (the PRESPEC estimand) cannot
   be identified. pyfixest dropped `fbs1` (see `results/logs/pia.log`). `e13lib.run_channel` then averaged only the
   terms left (`cols = [c for c in pn if c in mp.coef().index]`) without saying so. The reported "+0.74%
   [-0.87, +2.38], placebo passes" is really fake lag 0 alone, which measures the one-year change from 2017-18 to
   2018-19 (a pre-trend check of sorts, not the pre-specified placebo). The same applies to PIA log earners and log
   median. Fix: report the PIA placebo as "not estimable (only 2 pre-fire years)" and set `placebo_pass` to blank
   or false for the PIA rows. The PIA verdict stays "suggestive (down)" (it is secondary, and its COVID check
   already says "no pre-COVID estimate"). But the write-up must not say the PIA -1.65% "passes the placebo". The
   code should also raise an error rather than silently average a subset of terms. The only other dropped variable
   in any log is a control (`o1`, businesses binary-dose run), which is harmless.

2. **Unemployment B placebo fails (no error; the reading needs care).** The audit gets the same failing placebo
   (-0.195 points [-0.36, -0.03]). `summarise.py` already labels it "fails: placebo". That is correct under the rules.
   It means exposed SA2s already had falling unemployment relative to their region before Black Summer. So the B
   estimate cannot be separated from regional shocks, as the PRESPEC says.

3. **Suburb name rule drops 172 BOCSAR suburbs that could be matched (changes a number a little; no verdict
   change).** BOCSAR writes qualified names like "Back Creek (Bland)". SAL 2021 writes "Back Creek (Bland - NSW)".
   The locked rule removes the bracket from both and then drops the name as ambiguous. That follows the PRESPEC
   exactly, so it is not a deviation. But all 172 qualified BOCSAR names match a SAL name exactly once " - NSW" is
   removed: 71 have >= 50 dwellings and 8 had Black Summer H >= 1%. Post-hoc, adding them moves DV sample B from
   -0.46% [-3.24, +2.41] to -0.94% [-3.64, +1.84]. That is still "not detected". It can be reported as a post-hoc
   sensitivity check.

4. **Unemployment panel is unbalanced (cosmetic).** SALM has 438-439 NSW SA2s up to 2019Q1, 500 to 2023Q2 and 623
   after. The 184 late-entering SA2s are almost all unexposed: every SA2 with Black Summer H >= 1% has data from
   2010. So this does not drive the result, but the write-up should say the panel is unbalanced (the PRESPEC does
   not require balance here).

5. **Cosmetic points.**
   - The PRESPEC P placebo says "same model". The main code fits the P placebo with only the two fake lags and no
     real-dose controls. That is defensible because post-fire area-years are dropped. Adding real lags 0-3 as
     controls gives +0.95% [-1.62, +3.58] instead of +0.92% [-1.65, +3.56] for ATO P, so it makes no difference.
   - One postcode's SA4 (the SA4 with most of its dwellings) is not the parent SA4 of its SA3. This follows the
     "most dwellings" rule exactly, and the effect is negligible.
   - `units_poa.parquet` has one postcode with 0 dwellings. It is removed in `add_regions`, as the PRESPEC says.
   - pyfixest drops singleton fixed effects, and Poisson drops separated observations, by default. These defaults
     are not mentioned in the PRESPEC. They do not change point estimates (OLS) or are standard practice (Poisson).
   - `check_lock()` checks only the PRESPEC hash, not the code hashes.
   - Result tables label years by their start (e.g. "2014-2022"). The write-up should say 2014-15 to 2022-23.

## 4. What the audit could not check
- The mesh-block shares inside the fire outlines (`mb_fy_shares`) were taken as given. The outline geometry and
  the fire-file sources were not re-intersected.
- Businesses (CABEE), postcode DV, the R/S doses, the binary and GCCSA secondary runs, and the property channel were
  not re-derived.

## 5. Bottom line
Every primary and secondary number the audit re-derived matches the main analysis to the reported precision. The
only exception is the PIA placebo, which cannot be estimated with two pre-fire years and should not be reported as
passing. No issue found changes a primary verdict. All ten primary tests remain "not detected at this scale" (all
Holm p = 1.0). The pre-specification was not changed after the lock, and the one post-lock code edit is the
documented business-code fix.
