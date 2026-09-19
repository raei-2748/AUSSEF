# AUSSEF experiments

The repository is organised around four numbered experiments. Each experiment has one clear entry notebook and keeps its data, evidence and outputs inside its own folder.

| Experiment | Main question | Status | Start here |
|---|---|---|---|
| 1 | Can pre-disaster fiscal condition and disaster exposure predict a council's next-year fiscal condition? | Completed; the shallow tree did not beat persistence consistently. | [Experiment 1 notebook](Experiment%201/experiment.ipynb) |
| 2 | Does a longer matched fiscal and disaster history improve out-of-time prediction? | Completed; no consistent gain over persistence. | [Experiment 2 notebook](Experiment%202/experiment.ipynb) |
| 3 | Can public data measure whether disasters crowd out planned ordinary infrastructure spending? | Feasibility study; current measures are not sufficient for causal modelling. | [Experiment 3 notebook](Experiment%203/experiment.ipynb) |
| 4 | Do disasters cause abnormal downward revisions to pre-planned ordinary infrastructure spending, especially for fiscally weaker councils? | Focused pilot; quarterly revisions are partly recoverable, but matched ordinary year-end outcomes are not yet adequate for modelling. | [Experiment 4 notebook](Experiment%204/experiment.ipynb) |

## Folder guide

- `Experiment 1/` contains the original forecasting experiment.
- `Experiment 2/` contains the extended-history forecasting experiment and Version 2 panels.
- `Experiment 3/` contains the infrastructure crowd-out measurement study.
- `Experiment 4/` contains the current quarterly budget-reallocation pilot, its preceding audit, and preserved related funding-access studies.
- `NSW Data Panel.csv` is the untouched original source dataset.
- `graphify-out/` is an automatically maintained repository index, not an experiment.

The numbered experiment folders are the supported entry points. Historical evidence, source documents, manifests and detailed outputs remain within the experiment that produced them. Existing analytical conclusions were preserved during this reorganisation; no model was refitted.
