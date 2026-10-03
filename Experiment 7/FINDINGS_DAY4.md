# Experiment 7, Day 4: does a better "dose", pooling and quarterly data reveal the socioeconomic signal?

Date: 1 Oct 2026. Rules locked first: `PRESPEC_DAY4.md` (LOCK_DAY4.txt). Script: `day4_blurry.py`.

## Short answer
No signal detected. With the dose measured as the share of residents living in or within 1 km of the fire, all
218 rows pooled, and quarterly welfare data, none of the 6 indicators (or their average) rises with the dose, and no
pre-trend explains it away. Per the prespec, option 4 (per-fire estimates with ranges) was not run.

## What the pooled data can rule out (upper end of the 95% interval, per 10% of residents affected)
| Indicator | Best estimate | Effects larger than this are ruled out |
|---|---|---|
| Total personal income (fall) | 0.4% | 1.6% |
| Number of businesses (fall) | -0.5% | 0.1% |
| Council cash reserves (drawdown) | 0.45 months | 1.3 months |
| Services share of spending (squeeze) | -0.2 points | 0.5 points |
| Asset renewals ratio (rise) | 3 points | 19 points |
| Income-support recipients (rise, quarterly) | 0.1 per 1,000 | 0.7 per 1,000 |
Composite (average of all six, SD units): +0.013 [-0.03, +0.05] per 10% of residents affected.

The same holds with residents inside the fire only, with area burned as the dose, and without Black Summer.

## What it means
- Council-wide effects of the size people usually imagine are ruled out: e.g. a fire touching 10% of residents does
  not cut council income by more than about 1.6%, or add more than about 1 income-support claim per 1,000 people.
- Effects of the size the literature reports for affected people (Black Saturday: -8% income for employed people in
  affected areas) would be about 0.8% council-wide when 10% are affected: inside our range, too small to detect.
- So the honest result is a bound, not a zero: council statistics can only show effects above these sizes. Smaller,
  real effects need data on the affected people themselves (small areas or individuals).
