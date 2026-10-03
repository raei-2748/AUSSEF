"""Log a searched / viewed web page (not a download) to the bibliography part for one council.
usage: python3 bib_add.py --region-id ID --title T --publisher P --url U --type web_page|government_page
        --used-in "searched, not used"|"Experiment 10/B_qbrs" --purpose TEXT [--notes TEXT] [--year Y]"""
import argparse, os, sys, datetime, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from common import *
a = argparse.ArgumentParser()
for k in ["region-id","title","publisher","url","type","used-in","purpose"]: a.add_argument("--"+k, required=True)
a.add_argument("--notes", default=""); a.add_argument("--year", default="")
x = a.parse_args()
append_row(os.path.join(B, "work", str(x.region_id), "bib.csv"), BIB_COLS, dict(
    source_id=f"exp10B_{x.region_id}_w{hashlib.sha1(x.url.encode()).hexdigest()[:10]}", title=x.title,
    author_or_publisher=x.publisher, year=x.year, source_type=x.type, url=x.url, accessed_date=datetime.date.today().isoformat(),
    used_in=x.used_in, what_it_was_used_for=x.purpose, notes=x.notes))
print("ok")
