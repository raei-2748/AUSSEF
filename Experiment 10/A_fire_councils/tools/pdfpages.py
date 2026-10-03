#!/usr/bin/env python3
"""Find pages in a PDF whose text matches keywords; or dump text of given pages.
usage: pdfpages.py FILE find "kw1|kw2|regex"      -> prints page numbers (1-based PDF index) + matching lines
       pdfpages.py FILE dump 12 13 14               -> prints text of those pages
       pdfpages.py FILE info                        -> page count
"""
import sys, re, pypdf
f, mode = sys.argv[1], sys.argv[2]
r = pypdf.PdfReader(f)
if mode == "info":
    print("pages", len(r.pages)); sys.exit()
if mode == "find":
    pat = re.compile(sys.argv[3], re.I)
    for i, p in enumerate(r.pages, 1):
        try: t = p.extract_text() or ""
        except Exception as e: t = ""
        hits = [l.strip() for l in t.splitlines() if pat.search(l)]
        if hits:
            print(f"--- page {i}")
            for h in hits[:12]: print("   ", h[:200])
elif mode == "dump":
    for n in sys.argv[3:]:
        print(f"===== page {n}"); print(r.pages[int(n)-1].extract_text())
