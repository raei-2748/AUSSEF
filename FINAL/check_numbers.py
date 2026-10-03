"""Check every number in CORE_NUMBERS.csv against its source file, and every bibliography id against the merged
bibliography. Ray's rule: no number in the project without a source file and a bibliography entry.
Run: python3 FINAL/check_numbers.py   (exit code 1 if anything fails)"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
core = pd.read_csv(ROOT / "FINAL/CORE_NUMBERS.csv", dtype={"locator": str, "column": str, "bib_ids": str})
bib = pd.read_csv(ROOT / "bibliography/BIBLIOGRAPHY.csv", dtype=str).fillna("")
known = set(bib.source_id) | {i.strip() for m in bib.merged_ids for i in m.replace(",", ";").replace("|", ";").split(";") if i.strip()}

fails = 0
for r in core.itertuples():
    src = ROOT / r.source_file
    try:
        if r.kind == "csv":
            rows = pd.read_csv(src).query(r.locator)
            assert len(rows) == 1, f"locator matched {len(rows)} rows"
            got = float(rows[r.column].iloc[0])
        else:
            node = json.loads(src.read_text())
            for k in r.locator.split("/"):
                node = node[int(k)] if isinstance(node, list) else node[k]
            got = float(node)
        ok_val = abs(got - r.value) <= r.tol
    except Exception as e:  # noqa: BLE001
        got, ok_val = f"ERROR {e}", False
    ids = [i for i in str(r.bib_ids).split(";") if i and i != "nan"]
    missing = [i for i in ids if i not in known]
    ok = ok_val and ids and not missing
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {r.id} {r.display:<22} source={got if not ok_val else 'ok'}"
          f"{'' if ids else ' NO BIB IDS'}{' missing ids: ' + ','.join(missing) if missing else ''}")
print(f"\n{len(core) - fails} of {len(core)} pass")
sys.exit(1 if fails else 0)
