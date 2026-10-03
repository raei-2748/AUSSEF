"""Append source rows to bibliography/parts/exp15_nightlights_2026-10-02.csv (format: bibliography/README.md)."""
import csv
import hashlib
import os
from pathlib import Path

ROOT = Path("/Users/ray/Research/AUSSEF - Local")
PART = Path(__file__).resolve().parents[2] / "bibliography/parts/exp15_nightlights_2026-10-02.csv"
COLS = ["source_id", "title", "author_or_publisher", "year", "source_type", "url", "doi", "accessed_date",
        "local_path", "bytes", "sha256", "used_in", "what_it_was_used_for", "pages_or_table", "quote_or_value",
        "notes"]


def existing():
    if not PART.exists():
        return []
    with open(PART, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add(**kw):
    rows = existing()
    if any(r["source_id"] == kw["source_id"] for r in rows):
        return
    kw.setdefault("accessed_date", "2026-10-02")
    kw.setdefault("used_in", "Experiment 15_nightlights")
    lp = kw.get("local_path", "")
    if lp and not kw.get("sha256"):
        here = Path(__file__).resolve().parents[2]  # worktree copy of the project (Experiment 15 lives here for now)
        p = Path(lp) if os.path.isabs(lp) else (here / lp if (here / lp).exists() else ROOT / lp)
        if p.is_file():
            kw["bytes"] = p.stat().st_size
            kw["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
    new = not PART.exists()
    with open(PART, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, COLS)
        if new:
            w.writeheader()
        w.writerow({c: kw.get(c, "") for c in COLS})


def update(source_id, **kw):
    """Edit fields of an existing row (used for audit fixes)."""
    rows = existing()
    for r in rows:
        if r["source_id"] == source_id:
            r.update({k: str(v) for k, v in kw.items()})
    with open(PART, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        w.writerows(rows)
