# Rebuild and verify the Experiment 4 evidence store

Run `python3 rebuild_evidence.py /absolute/path/to/a/new/output_directory` from this folder. The destination must not exist. The runner applies all fifteen source-import and audit stages in their required order, checks database integrity and foreign keys, compares every database table with its CSV export, and compares the rebuilt table contents against the current canonical store. It never fits a model or overwrites the canonical data.

The verified rebuild reproduced all21 tables exactly:62 project candidates,375 snapshot slots,136 reported amounts,160 source records (including duplicate document registrations), and zero certified model rows. The104 council lookup entries and1339 inherited annual fiscal records do not imply equivalent project coverage. Disaster table rows include unresolved aliases and are not an independent event count.

`rebuild_verification.json` records this result. Passing reproducibility checks establishes computational consistency only: it does not certify project scope, original adoption, expenditure comparability, exposure, publication vintage, controls or causal identification. See the field-specific audits for those open gates.

Raw inputs and earlier experiment outputs are read-only to the runner. Network access is not required because the currently used sources are preserved locally. Hard-coded repository paths in existing stages require this repository at /Users/ray/Research/AUSSEF.
