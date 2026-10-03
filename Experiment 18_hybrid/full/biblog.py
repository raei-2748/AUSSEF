"""Append rows to the Experiment 18 bibliography part (skips ids already present)."""
import csv
import hashlib
from pathlib import Path

ROOT = Path("/Users/ray/Research/AUSSEF - Local")
BIB = ROOT / "bibliography/parts/exp18_hybrid_2026-10-03.csv"
COLS = ["source_id", "title", "author_or_publisher", "year", "source_type", "url", "doi", "accessed_date", "local_path",
        "bytes", "sha256", "used_in", "what_it_was_used_for", "pages_or_table", "quote_or_value", "notes"]


def log(source_id, title, local_path, used_for, table="", value="", notes="", author="Ray Wang (AUSSEF project)",
        year="2026", stype="dataset", url="", date="2026-10-03"):
    have = {r["source_id"] for r in csv.DictReader(open(BIB))}
    if source_id in have:
        return
    p = ROOT / local_path if local_path else None
    size = sha = ""
    if p is not None and p.is_file():
        size = p.stat().st_size
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
    with open(BIB, "a", newline="") as f:
        csv.writer(f).writerow([source_id, title, author, year, stype, url, "", date, local_path, size, sha,
                                "Experiment 18_hybrid (full build)", used_for, table, value, notes])
