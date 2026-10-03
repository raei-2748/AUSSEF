"""Dump PDF text per page (1-based page numbers = PDF page index).
usage: python3 pdf_pages.py FILE.pdf [--grep REGEX] [--pages 3-7]"""
import argparse, re, sys
from pypdf import PdfReader
a = argparse.ArgumentParser(); a.add_argument("file"); a.add_argument("--grep"); a.add_argument("--pages")
x = a.parse_args()
rd = PdfReader(x.file); N = len(rd.pages)
rng = range(1, N + 1)
if x.pages:
    s, _, e = x.pages.partition("-"); rng = range(int(s), int(e or s) + 1)
print(f"# {x.file}: {N} pages")
for i in rng:
    if i < 1 or i > N: continue
    try: t = rd.pages[i - 1].extract_text(extraction_mode="layout") or ""
    except Exception: t = rd.pages[i - 1].extract_text() or ""
    if x.grep:
        hits = [l for l in t.splitlines() if re.search(x.grep, l, re.I)]
        if hits: print(f"\n=== page {i} ({len(hits)} hits)\n" + "\n".join(hits[:15]))
    else:
        print(f"\n=== page {i}\n{t}")
