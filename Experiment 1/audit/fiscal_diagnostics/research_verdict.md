# Research verdict

All comparisons are exploratory, on the same three previously inspected operating-ratio outcome years.

- persistence: pooled MAE 6.938 pp; RMSE 9.028 pp; R² 0.116; MAE wins over persistence 0/3.

- tree_level: pooled MAE 7.400 pp; RMSE 9.291 pp; R² 0.063; MAE wins over persistence 0/3.

- tree_fiscal_only: pooled MAE 7.400 pp; RMSE 9.291 pp; R² 0.063; MAE wins over persistence 0/3.

- tree_change: pooled MAE 7.215 pp; RMSE 9.257 pp; R² 0.070; MAE wins over persistence 1/3.

- ridge_level: pooled MAE 7.104 pp; RMSE 9.125 pp; R² 0.096; MAE wins over persistence 1/3.

- ridge_change: pooled MAE 7.328 pp; RMSE 9.413 pp; R² 0.038; MAE wins over persistence 1/3.

- mean_change: pooled MAE 8.032 pp; RMSE 10.264 pp; R² -0.143; MAE wins over persistence 0/3.

- training_mean: pooled MAE 7.517 pp; RMSE 9.991 pp; R² -0.083; MAE wins over persistence 0/3.


**A. Better than persistence?** No tested model establishes consistent superiority on both pooled errors and all three annual MAEs. See every model above; a partial gain is not suppressed.

**B. Disaster increment?** The fiscal-only and fiscal-plus-disaster trees differ in 0 held-out predictions at tolerance 1e-10; 0 disaster splits. This tests tree ablation only; ridge exposure ablation was not requested and has not been tested. No causal conclusion follows.

**C. Predict change?** Tree change versus tree level MAE: 7.215 versus 7.400 pp. Ridge change versus ridge level: 7.328 versus 7.104 pp. Compare each with persistence and individual-year results.

**D. Ridge and coarse predictions?** Ridge produces continuous predictions, but removal of tree bands does not itself validate forecasts. Here ridge level reduces pooled MAE from 7.400 to 7.104 pp, but persistence remains better at 6.938 pp. Thus it helps relative to the tree but does not solve the forecasting problem. Early alpha selection uses training-only council groups because temporal inner validation is impossible; the latest fold uses an inner forward test.

**E. More complex ML? NO-GO at this stage.** Few temporal blocks, retrospective data availability and reused holdouts do not justify increasing complexity. Modest comparator gains, if any, require an untouched future evaluation, not further selection on these years.

**F. Data next?** First verify availability/definitions; extend comparable fiscal history; audit underlying operating revenue/expense and separate grant recognition/receipt timing; then improve physical flood and forecast-time damage measurements, and distinguish routine maintenance from reconstruction. See data_gap_priorities.md.