#!/usr/bin/env python3
"""Discard a wrongly downloaded file (wrong council/year/document): deletes the PDF, sets its downloads_log status to
'discarded' (keeps the row, so the URL stays on record), and moves its bibliography row to used_in='searched, not used'.

Usage: python3 discard.py --local-path fire_event_dataset/.../x.pdf --reason "was the auditor's report only"
"""
import argparse, csv, fcntl, os

ROOT = "/Users/ray/Research/AUSSEF - Local"
EXP = os.path.join(ROOT, "Experiment 10", "A_comparison_councils")
LOG = os.path.join(EXP, "downloads_log.csv")
BIB = os.path.join(EXP, "work", "bib", "downloads_bib.csv")
LOCK = os.path.join(EXP, "work", ".dl.lock")

p = argparse.ArgumentParser()
p.add_argument("--local-path", required=True)
p.add_argument("--reason", required=True)
a = p.parse_args()
with open(LOCK, "a") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    for path, fn in ((LOG, "log"), (BIB, "bib")):
        with open(path, encoding="utf-8") as f:
            r = csv.DictReader(f); cols = r.fieldnames; rows = list(r)
        hit = 0
        for row in rows:
            if row["local_path"] == a.local_path:
                hit += 1
                if fn == "log":
                    if row["status"] == "downloaded":
                        row["status"] = "discarded"
                    row["note"] = (row["note"] + "; " if row["note"] else "") + "discarded: " + a.reason
                else:
                    row["used_in"] = "searched, not used"
                    row["notes"] = (row["notes"] + "; " if row["notes"] else "") + "downloaded then discarded: " + a.reason
                    row["local_path"] = ""
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
        print(f"{fn}: {hit} row(s) updated")
    full = os.path.join(ROOT, a.local_path)
    if os.path.exists(full):
        os.remove(full); print("deleted", a.local_path)
