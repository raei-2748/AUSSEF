#!/usr/bin/env python3
"""Per-page text of a PDF (pypdf layout mode), cached in work/text/.

Usage:
  python3 pdftext.py FILE.pdf                       # build cache; prints cache path, page count, empty-page count
  python3 pdftext.py FILE.pdf --grep "regex"        # PAGE <n>: <line> for matching lines (case-insensitive)
  python3 pdftext.py FILE.pdf --page 12 --page 13   # full text of those pages
FILE may be absolute or relative to /Users/ray/Research/AUSSEF - Local.
Page numbers are 1-based PDF page indices (what a PDF viewer shows), NOT the printed page label.
If most pages are empty the PDF is scanned: read those pages visually with the Read tool (pages="n").
"""
import argparse, hashlib, os, re
from pypdf import PdfReader

CACHE = "/Users/ray/Research/AUSSEF - Local/Experiment 10/A_comparison_councils/work/text"
ROOT = "/Users/ray/Research/AUSSEF - Local"


def load(path):
    path = path if os.path.isabs(path) else os.path.join(ROOT, path)
    key = hashlib.sha1(path.encode()).hexdigest()[:10] + "_" + os.path.basename(path) + ".pages.txt"
    cp = os.path.join(CACHE, key)
    if not os.path.exists(cp):
        r = PdfReader(path)
        out = []
        for i, pg in enumerate(r.pages, 1):
            try:
                t = pg.extract_text(extraction_mode="layout")
            except Exception:
                try:
                    t = pg.extract_text()
                except Exception as e:
                    t = f"[extract error {e}]"
            out.append(f"\f=== PAGE {i} ===\n{t or ''}")
        os.makedirs(CACHE, exist_ok=True)
        with open(cp + ".tmp", "w", encoding="utf-8") as f:
            f.write("".join(out))
        os.replace(cp + ".tmp", cp)
    d = {}
    for blk in open(cp, encoding="utf-8").read().split("\f=== PAGE ")[1:]:
        n, _, body = blk.partition(" ===\n")
        d[int(n)] = body
    return cp, d


p = argparse.ArgumentParser()
p.add_argument("file")
p.add_argument("--grep")
p.add_argument("--page", type=int, action="append")
a = p.parse_args()
cp, d = load(a.file)
if a.grep:
    rx = re.compile(a.grep, re.I)
    for n in sorted(d):
        for line in d[n].splitlines():
            if rx.search(line):
                print(f"PAGE {n}: {re.sub(r' {3,}', '   ', line.strip())}")
elif a.page:
    for n in a.page:
        print(f"=== PAGE {n} ===\n{d.get(n, '[no such page]')}")
else:
    empty = sum(1 for v in d.values() if len(v.strip()) < 30)
    print(f"cache={cp}\npages={len(d)} empty_pages={empty}")
