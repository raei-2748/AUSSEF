#!/usr/bin/env python3
"""Log a web page that was searched/visited (not downloaded) to work/bib/searched_bib.csv.

Usage: python3 logsrc.py --url URL --title "..." --publisher "X Council" [--used-in "searched, not used"] \
          [--what "listing page of financial statements"] [--notes "link failed 2026-10-02"] [--type government_page]
"""
import argparse, csv, datetime, fcntl, os

EXP = "/Users/ray/Research/AUSSEF - Local/Experiment 10/A_comparison_councils"
BIB = os.path.join(EXP, "work", "bib", "searched_bib.csv")
COLS = ["source_id", "title", "author_or_publisher", "year", "source_type", "url", "doi", "accessed_date",
        "local_path", "bytes", "sha256", "used_in", "what_it_was_used_for", "pages_or_table", "quote_or_value", "notes"]

p = argparse.ArgumentParser()
p.add_argument("--url", required=True)
p.add_argument("--title", required=True)
p.add_argument("--publisher", required=True)
p.add_argument("--used-in", default="searched, not used")
p.add_argument("--what", default="")
p.add_argument("--notes", default="")
p.add_argument("--type", default="government_page")
a = p.parse_args()
os.makedirs(os.path.dirname(BIB), exist_ok=True)
with open(BIB + ".lock", "a") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    new = not os.path.exists(BIB)
    with open(BIB, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerow(dict(title=a.title, author_or_publisher=a.publisher, source_type=a.type, url=a.url,
                        accessed_date=datetime.date.today().isoformat(), used_in=a.used_in,
                        what_it_was_used_for=a.what, notes=a.notes))
print("logged")
