"""Guarded downloader for QBRS PDFs.
usage: python3 download.py --region-id 10550 --council "Bega Valley" --fy 2019-20 --quarter Q2 \
         --url URL --found-on PAGE_URL --name SHORT_NAME [--notes TEXT]
Rules enforced: official hosts only (*.nsw.gov.au, *.gov.au, or a council's vendor portal such as *.infocouncil.biz
when --found-on is an official *.nsw.gov.au page); each file <= 40 MB; per-council folder <= 50 MB (was 120 MB for the first 49 councils);
whole qbrs folder hard stop at 3.6 GB. Appends to work/<region_id>/downloads_log.csv and bibliography part.
Prints JSON result."""
import argparse, hashlib, json, os, sys, datetime, urllib.parse, requests
sys.path.insert(0, os.path.dirname(__file__))
from common import *
MAXF = 40 * 1024**2; MAXC = 50 * 1024**2; MAXG = int(3.6 * 1024**3)  # MAXC lowered from 120 MB after first 49 councils used 1.3 GB
VENDOR = (".infocouncil.biz", ".openoffice.com.au")
a = argparse.ArgumentParser()
for k in ["region-id","council","fy","quarter","url","found-on","name"]: a.add_argument("--"+k, required=True)
a.add_argument("--notes", default="")
x = a.parse_args()
today = datetime.date.today().isoformat()
host = urllib.parse.urlparse(x.url).hostname or ""
fo_host = urllib.parse.urlparse(x.found_on).hostname or ""
ok_host = host.endswith(".gov.au") or (host.endswith(VENDOR) and fo_host.endswith(".nsw.gov.au"))
log = os.path.join(B, "work", str(x.region_id), "downloads_log.csv")
base = dict(region_id=x.region_id, council=x.council, fy=x.fy, quarter=x.quarter, url=x.url, found_on=x.found_on,
            accessed_date=today, notes=x.notes)
def done(status, **kw):
    r = dict(base, status=status, **kw); append_row(log, DL_COLS, r); print(json.dumps(r)); sys.exit(0)
if not ok_host: done("refused_non_official_host")
cdir = os.path.join(PDF_ROOT, str(x.region_id))
if dir_bytes(PDF_ROOT) > MAXG: done("refused_global_4GB_guard_STOP")
if dir_bytes(cdir) > MAXC: done("refused_council_cap_120MB")
try:
    r = requests.get(x.url, stream=True, timeout=90, headers={"User-Agent": "Mozilla/5.0 (research; AUSSEF student project)"})
except Exception as e: done("failed", notes=f"{x.notes} | error {e!r}"[:300])
if r.status_code != 200: done(f"http_{r.status_code}")
cl = int(r.headers.get("Content-Length") or 0)
if cl > MAXF: done("skipped_over_40MB", bytes=cl)
os.makedirs(cdir, exist_ok=True)
safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in x.name)[:80]
fn = f"{x.region_id}_FY{x.fy}_{x.quarter}_{safe}"
if not fn.lower().endswith(".pdf"): fn += ".pdf"
path = os.path.join(cdir, fn); h = hashlib.sha256(); n = 0
with open(path + ".part", "wb") as f:
    for ch in r.iter_content(1 << 16):
        n += len(ch)
        if n > MAXF:
            f.close(); os.remove(path + ".part"); done("skipped_over_40MB", bytes=n)
        h.update(ch); f.write(ch)
with open(path + ".part", "rb") as f: head = f.read(5)
if head != b"%PDF-":
    os.remove(path + ".part"); done("not_a_pdf", bytes=n, notes=f"{x.notes} | content-type {r.headers.get('Content-Type')}")
os.replace(path + ".part", path)
rel = os.path.relpath(path, ROOT)
append_row(os.path.join(B, "work", str(x.region_id), "bib.csv"), BIB_COLS, dict(
    source_id=f"exp10B_{x.region_id}_{h.hexdigest()[:10]}", title=f"{x.council} Council quarterly budget review statement {x.fy} {x.quarter} ({x.name})",
    author_or_publisher=f"{x.council} Council", year="", source_type="budget_review", url=x.url, accessed_date=today,
    local_path=rel, bytes=n, sha256=h.hexdigest(), used_in="Experiment 10/B_qbrs", what_it_was_used_for="QBRS extraction",
    notes=f"found on {x.found_on}. {x.notes}"))
done("downloaded", local_path=rel, bytes=n, sha256=h.hexdigest())
