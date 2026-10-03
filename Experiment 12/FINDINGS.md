# Experiment 12 findings: spillover to neighbouring councils, and per-home bounds

2 Oct 2026. Rules locked first (PRESPEC.md, LOCK.txt). Scripts: adjacency.py, run_spillover.py; post-hoc checks
(added after seeing Part A, NOT pre-registered): posthoc_checks.py. No downloads.

## Part A (pre-registered): did unburned NEIGHBOURS of councils that lost 5+ homes rise more than far councils?
36 neighbour x season units (20 of them Black Summer), 33 councils.

| Outcome | Neighbour minus far councils [95% CI] | Holm p | Link with homes destroyed next door | Verdict |
|---|---|---|---|---|
| Rents (year 2) | **+7.0% [+4.2, +9.7]** | 0.003 | rho +0.45 | Detected |
| Income-support recipients (months 4-12) | **+3.5% [+1.3, +6.3]** | 0.007 | rho +0.35 | Detected |
| Domestic violence (year 2) | -0.8% [-8.0, +6.2] | 0.84 | rho +0.11 | Not detected |

## Post-hoc checks (not pre-registered) change how far Part A can be trusted
- **Income support:** with fake fire dates 24 months EARLIER (placebo), neighbours already rose +2.5% [+1.4, +3.7]
  more than far councils. Most of the +3.5% is a pre-existing trend (neighbours are mostly coastal/eastern councils,
  far councils mostly inland/western). **Not credible as a fire spillover.**
- **Rents:** the placebo cannot be run (rent data start in 2017; only 4 units). Outside Black Summer the gap is still
  positive but weak: +4.8% [+0.6, +10.0], 9 units, p = 0.08 (2017 fires +14.7%, 2018 +2.6%, 2023 +1.4%). Black
  Summer's year 2 overlaps the 2020-21 regional rent boom, which was strongest in coastal councils.
  **Suggestive, not proven:** the pattern fits displaced households pushing up rents next door, and it is stronger
  next to bigger losses (rho +0.45), but a coastal rent boom could produce part of it.
- **Domestic violence:** the placebo shows +8% (noise level); nothing to read.

## Part B (pre-registered sensitivity): burned councils compared with FAR councils only
Rents: link with fire size rises from +0.18 (Experiment 11, all unburned councils as comparison) to **+0.27**.
DV: +0.03 to +0.04 (no change). Consistent with neighbours pulling the rent comparison toward zero.

## Part C (pre-registered, descriptive): the largest effect per destroyed home the data allow
| Measure (burned councils) | Slope [95% CI] | Reading |
|---|---|---|
| Council median rent, year 2 | **+2.2% per 100 homes destroyed [+1.5, +5.6]** | Rents rise with homes lost (CI excludes 0; Black Summer-heavy) |
| Domestic-violence incidents per year | +0.07 per destroyed home [-0.00, +0.24] | At most about 1 extra incident a year per 4 homes lost |
| Income-support recipients | +1.3 per destroyed home [-0.04, +4.5] | At most about 4-5 extra recipients per home lost |

## What it means
Rents are the household channel most likely to be real but hidden: they rise with homes lost in the burned council
and, more weakly, in its neighbours, and the comparison with neighbours partly hid it. Income support and domestic
violence stay unconvincing. The rent result cannot be separated cleanly from the 2020-21 regional rent boom.
