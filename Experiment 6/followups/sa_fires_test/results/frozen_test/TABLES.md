### SA row table (score, pillars, coverage)

| Event | Council | Burned % | Homes destroyed (status) | Blocks | risk_add_avail | V | DL | IL | FP | SL | pillars | Y_new |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pinery 2015 | Light (RegC) | 29.7 | 41 (reported) | HEV | 0.34 | 0.23 | 0.92 | 0.13 | 0.88 | 0.08 | 4 | 0.50 |
| Pinery 2015 | Mallala (DC) | 13.8 | 15 (reported) | HEV | 0.45 | 0.33 | 0.85 | 0.25 | 0.52 | 0.58 | 4 | 0.55 |
| Pinery 2015 | Wakefield (DC) | 5.3 | 36 (reported) | V | 0.61 | 0.61 | 0.93 | 0.66 | 0.50 | 0.27 | 4 | 0.59 |
| Pinery 2015 | Clare and Gilbert Valleys (DC) | 5.0 | 5 (reported) | V | 0.33 | 0.33 | 0.75 | 0.21 | 0.64 | 0.05 | 4 | 0.41 |
| Sampson Flat 2015 | Adelaide Hills (DC) | 11.7 | blank | HEV | 0.69 | 0.14 |  | 0.39 | 0.48 | 0.08 | 3 | 0.32 |
| Sampson Flat 2015 | Playford (C) | 5.5 | blank | HEV | 0.63 | 0.79 |  | 0.36 | 0.46 | 0.92 | 3 | 0.58 |
| Sampson Flat 2015 | Tea Tree Gully (C) | 3.2 | blank | HEV | 0.31 | 0.20 |  | 0.67 | 0.47 | 0.22 | 3 | 0.45 |
| Kangaroo Island 2019-20 | Kangaroo Island (DC) | 45.7 | blank | HEV | 0.81 | 0.58 |  | 0.30 | 0.67 | 0.05 | 3 | 0.34 |
| Keilira 2019-20 | Kingston (DC) (SA) | 6.8 | 3 (reported) | V | 0.46 | 0.46 | 0.78 | 0.35 | 0.44 | 0.95 | 4 | 0.63 |
| Cudlee Creek 2019 | Adelaide Hills (DC) | 18.3 | blank | HEV | 0.71 | 0.20 |  | 0.27 | 0.59 | 0.07 | 3 | 0.31 |
| Cudlee Creek 2019 | Mount Barker (DC) | 11.6 | blank | HEV | 0.82 | 0.46 |  | 0.19 | 0.46 | 0.71 | 3 | 0.45 |

### Tests

| Test | Scope | Score | Target | n | Spearman | 95% CI |
|---|---|---|---|---:|---:|---|
| PRIMARY | pooled | risk_add_avail | Y_new | 37 | -0.09 | [-0.42, +0.26] |
| primary_other_scope | SA_all | risk_add_avail | Y_new | 11 | -0.28 | [-0.72, +0.70] |
| primary_other_scope | stage1_only(reproduction check) | risk_add_avail | Y_new | 26 | 0.00 | [-0.41, +0.39] |
| primary_other_scope | pooled_without_SA_2019_20 | risk_add_avail | Y_new | 33 | 0.05 | [-0.30, +0.37] |
| primary_other_scope | SA_2015_events_only | risk_add_avail | Y_new | 7 | 0.18 | [-0.75, +1.00] |
| primary_other_scope | event:SA_2015_sampson_flat | risk_add_avail | Y_new | 3 |  | not estimable |
| primary_other_scope | event:SA_2015_pinery | risk_add_avail | Y_new | 4 |  | not estimable |
| primary_other_scope | event:SA_2019_cudlee_creek | risk_add_avail | Y_new | 2 |  | not estimable |
| primary_other_scope | event:SA_2019_20_kangaroo_island | risk_add_avail | Y_new | 1 |  | not estimable |
| primary_other_scope | event:SA_2019_20_keilira | risk_add_avail | Y_new | 1 |  | not estimable |
| pillar | pooled | risk_add_avail | DL | 16 | -0.58 | [-0.85, -0.14] |
| pillar | pooled | risk_add_avail | IL | 37 | 0.24 | [-0.12, +0.56] |
| pillar | pooled | risk_add_avail | FP | 24 | -0.15 | [-0.53, +0.30] |
| pillar | pooled | risk_add_avail | SL | 11 | 0.05 | [-0.70, +0.77] |
| secondary_S1_V | pooled | S1_V | Y_new | 37 | 0.26 | [-0.09, +0.55] |
| secondary_S2_HV | pooled | S2_HV | Y_new | 21 | 0.11 | [-0.34, +0.50] |
| secondary_S1_V_DL | pooled | S1_V | DL | 16 | -0.23 | [-0.75, +0.36] |
| pillar | SA_all | risk_add_avail | DL | 5 |  | not estimable |
| pillar | SA_all | risk_add_avail | IL | 11 | -0.09 | [-0.80, +0.70] |
| pillar | SA_all | risk_add_avail | FP | 11 | -0.12 | [-0.72, +0.62] |
| pillar | SA_all | risk_add_avail | SL | 11 | 0.05 | [-0.71, +0.78] |
| secondary_S1_V | SA_all | S1_V | Y_new | 11 | 0.65 | [-0.19, +0.89] |
| secondary_S2_HV | SA_all | S2_HV | Y_new | 8 | -0.07 | [-0.88, +0.68] |
| secondary_S1_V_DL | SA_all | S1_V | DL | 5 |  | not estimable |
| pillar | pooled_without_SA_2019_20 | risk_add_avail | DL | 15 | -0.58 | [-0.85, -0.14] |
| pillar | pooled_without_SA_2019_20 | risk_add_avail | IL | 33 | 0.43 | [+0.11, +0.67] |
| pillar | pooled_without_SA_2019_20 | risk_add_avail | FP | 20 | -0.28 | [-0.66, +0.21] |
| pillar | pooled_without_SA_2019_20 | risk_add_avail | SL | 7 | 0.43 | [-0.41, +1.00] |
| secondary_S1_V | pooled_without_SA_2019_20 | S1_V | Y_new | 33 | 0.26 | [-0.09, +0.56] |
| secondary_S2_HV | pooled_without_SA_2019_20 | S2_HV | Y_new | 18 | 0.17 | [-0.28, +0.58] |
| secondary_S1_V_DL | pooled_without_SA_2019_20 | S1_V | DL | 15 | -0.23 | [-0.76, +0.36] |
| pillar | SA_2015_events_only | risk_add_avail | DL | 4 |  | not estimable |
| pillar | SA_2015_events_only | risk_add_avail | IL | 7 | 0.11 | [-0.76, +1.00] |
| pillar | SA_2015_events_only | risk_add_avail | FP | 7 | -0.36 | [-1.00, +0.65] |
| pillar | SA_2015_events_only | risk_add_avail | SL | 7 | 0.43 | [-0.61, +1.00] |
| secondary_S1_V | SA_2015_events_only | S1_V | Y_new | 7 | 0.75 | [-0.04, +1.00] |
| secondary_S2_HV | SA_2015_events_only | S2_HV | Y_new | 5 |  | not estimable |
| secondary_S1_V_DL | SA_2015_events_only | S1_V | DL | 4 |  | not estimable |
| sens_a_share_ge5pct | pooled | risk_add_avail | Y_new | 23 | -0.09 | [-0.50, +0.39] |
| sens_a_share_ge5pct_S1_V | pooled | S1_V | Y_new | 23 | 0.27 | [-0.20, +0.64] |
| sens_b_ge2_pillars | pooled | risk_add_avail | Y_new_ge2pillars | 26 | -0.28 | [-0.62, +0.12] |
| sens_c_no_FP | pooled | risk_add_avail | Y_new_noFP | 37 | -0.03 | [-0.36, +0.32] |
| sens_d_DL_reported_only | pooled | risk_add_avail | DL_reported_only | 10 | -0.14 | [-0.80, +0.59] |
| sens_a_share_ge5pct | SA_all | risk_add_avail | Y_new | 9 | -0.58 | [-0.92, +0.26] |
| sens_a_share_ge5pct_S1_V | SA_all | S1_V | Y_new | 9 | 0.67 | [-0.27, +0.88] |
| sens_b_ge2_pillars | SA_all | risk_add_avail | Y_new_ge2pillars | 11 | -0.28 | [-0.72, +0.70] |
| sens_c_no_FP | SA_all | risk_add_avail | Y_new_noFP | 11 | -0.24 | [-0.79, +0.71] |
| sens_d_DL_reported_only | SA_all | risk_add_avail | DL_reported_only | 5 |  | not estimable |
| sens_a_share_ge5pct | pooled_without_SA_2019_20 | risk_add_avail | Y_new | 19 | 0.17 | [-0.34, +0.61] |
| sens_a_share_ge5pct_S1_V | pooled_without_SA_2019_20 | S1_V | Y_new | 19 | 0.28 | [-0.16, +0.67] |
| sens_b_ge2_pillars | pooled_without_SA_2019_20 | risk_add_avail | Y_new_ge2pillars | 22 | -0.14 | [-0.55, +0.30] |
| sens_c_no_FP | pooled_without_SA_2019_20 | risk_add_avail | Y_new_noFP | 33 | 0.12 | [-0.24, +0.45] |
| sens_d_DL_reported_only | pooled_without_SA_2019_20 | risk_add_avail | DL_reported_only | 9 | -0.18 | [-0.82, +0.61] |
| sens_f_leave_out | pooled minus SA_2015_sampson_flat | risk_add_avail | Y_new | 34 | -0.09 | [-0.43, +0.25] |
| sens_f_leave_out | pooled minus SA_2015_pinery | risk_add_avail | Y_new | 33 | -0.14 | [-0.47, +0.22] |
| sens_f_leave_out | pooled minus SA_2019_cudlee_creek | risk_add_avail | Y_new | 35 | -0.04 | [-0.37, +0.30] |
| sens_f_leave_out | pooled minus SA_2019_20_kangaroo_island | risk_add_avail | Y_new | 36 | -0.04 | [-0.38, +0.30] |
| sens_f_leave_out | pooled minus SA_2019_20_keilira | risk_add_avail | Y_new | 36 | -0.08 | [-0.42, +0.27] |

### Planted-effect power

| Rows | n | planted rho | power (CI lower > 0) | chance CI upper < 0.30 |
|---|---:|---:|---:|---:|
| pooled primary rows | 37 | 0.0 | 2% | 40% |
| pooled primary rows | 37 | 0.1 | 8% | 21% |
| pooled primary rows | 37 | 0.2 | 20% | 7% |
| pooled primary rows | 37 | 0.3 | 40% | 2% |
| pooled primary rows | 37 | 0.4 | 67% | 0% |
| pooled primary rows | 37 | 0.5 | 91% | 0% |
| pooled primary rows | 37 | 0.6 | 99% | 0% |
| SA rows | 11 | 0.0 | 3% | 11% |
| SA rows | 11 | 0.1 | 4% | 6% |
| SA rows | 11 | 0.2 | 10% | 3% |
| SA rows | 11 | 0.3 | 15% | 2% |
| SA rows | 11 | 0.4 | 22% | 0% |
| SA rows | 11 | 0.5 | 35% | 0% |
| SA rows | 11 | 0.6 | 52% | 0% |
| pooled without SA 2019-20 | 33 | 0.0 | 3% | 37% |
| pooled without SA 2019-20 | 33 | 0.1 | 10% | 17% |
| pooled without SA 2019-20 | 33 | 0.2 | 18% | 7% |
| pooled without SA 2019-20 | 33 | 0.3 | 40% | 1% |
| pooled without SA 2019-20 | 33 | 0.4 | 64% | 0% |
| pooled without SA 2019-20 | 33 | 0.5 | 87% | 0% |
| pooled without SA 2019-20 | 33 | 0.6 | 97% | 0% |

### Rows still needed (80% power, Fisher approximation)

| true rho | rows needed | pooled rows now | further rows |
|---:|---:|---:|---:|
| 0.3 | 85 | 37 | 48 |
| 0.4 | 47 | 37 | 10 |
| 0.5 | 30 | 37 | 0 |
