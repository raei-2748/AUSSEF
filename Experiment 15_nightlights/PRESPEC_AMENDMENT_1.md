# PRESPEC Amendment 1: how the 95% intervals are made (written before any real radiance was read)

Date: 2 Oct 2026. PRESPEC.md is unchanged and stays locked (LOCK.txt). This amendment is locked separately
(LOCK_AMENDMENT_1.txt). No real `avg_rade9` value had been read at this point: `work/rad.npy` did not exist, and
every test below used made-up (synthetic) lights.

## Why
Before using real data, I ran the analysis code on made-up lights:
- each pixel gets its own brightness level, a season pattern and monthly noise;
- noise is shared within each 3 km block, as with local weather or events;
- either no fire effect, or a planted 30% drop on the South Coast in 2020-04..09.

Findings, over 12 made-up datasets with no planted effect:
- **The estimate is unbiased.** Average Early D for the South Coast was +0.002 (true 0). For Tathra it was +0.014,
  with a standard error of 0.013.
- **The planted −30% drop was recovered**: −0.364 against the true −0.357.
- **The pre-set 3 km block bootstrap gives intervals that are far too narrow for small, bunched groups.** Tathra's
  9 inside pixels sit in one or two blocks, so there is almost nothing to resample. Bootstrap intervals about 0.03
  wide excluded 0 in several null runs, but the true spread of the estimate was 0.045 (SD).

## Change
- **Main 95% interval.** It now comes from random placebo "pseudo-towns". In each of 1,000 draws:
  1. Start at a random control pixel.
  2. Take the nearest control pixels until the treated group's count in every brightness band is matched.
  3. Compute this pseudo-town's D against the remaining controls, with exactly the same formula.

  The interval is [D − 97.5th percentile of pseudo-town D, D − 2.5th percentile]. "Detected" means the interval
  excludes 0, which is the same as the real D lying outside the middle 95% of pseudo-towns. In the 12 null runs the
  pseudo-town spread matched the true spread: 0.042 vs 0.045 (Tathra), 0.0167 vs 0.0164 (South Coast).
- **The block bootstrap interval** is still computed and stored (`boot_lo`, `boot_hi`) but is not used for any
  verdict.
- **Gradient Q4 and placebo C1** use the same pseudo-town draws. Inside and 1-5 km pseudo-towns are drawn
  independently.
- **The "random placebo groups" robustness check** in PRESPEC was drawn by whole blocks. That check is now
  replaced by the main interval and is kept only as an extra summary.

Everything else in PRESPEC.md is unchanged: definitions, windows, fires, questions, reading rules and sensitivity
checks.
