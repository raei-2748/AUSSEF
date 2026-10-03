#!/usr/bin/env python3
"""Guarded downloader for Experiment 10 / A_comparison_councils.

Enforces Ray's guardrails: official hosts only (*.gov.au), <= 40 MB per file, session total <= 4 GB,
PDF-only, sha256 + bytes logged to downloads_log.csv and work/bib/downloads_bib.csv.

Usage (Bash with sandbox DISABLED, network needed):
  python3 dl.py --region-id 10050 --council Albury --fy 2019-20 --url URL \
      --source-page URL_OF_OFFICIAL_PAGE_LINKING_IT --title "Albury City Council GPFS 2019-20" \
      [--doc-kind gpfs|annual_report|other]
Exit codes: 0 ok / already / duplicate, 2 rejected or failed, 3 BUDGET_STOP (4 GB would be exceeded).
"""
import argparse, csv, fcntl, hashlib, os, re, sys, tempfile, urllib.parse, urllib.request, datetime

ROOT = "/Users/ray/Research/AUSSEF - Local"
EXP = os.path.join(ROOT, "Experiment 10", "A_comparison_councils")
LOG = os.path.join(EXP, "downloads_log.csv")
BIB = os.path.join(EXP, "work", "bib", "downloads_bib.csv")
LOCK = os.path.join(EXP, "work", ".dl.lock")
PDF_ROOT = os.path.join(ROOT, "fire_event_dataset", "data", "raw", "council_pdfs", "financial_statements")
MAX_FILE = 40 * 1024 * 1024
MAX_TOTAL = 4 * 1024 ** 3
LOG_COLS = ["region_id", "council", "fy", "doc_kind", "title", "url", "source_page", "bytes", "sha256",
            "local_path", "accessed_date", "status", "note"]
BIB_COLS = ["source_id", "title", "author_or_publisher", "year", "source_type", "url", "doi", "accessed_date",
            "local_path", "bytes", "sha256", "used_in", "what_it_was_used_for", "pages_or_table", "quote_or_value", "notes"]


def official(host):
    return (host or "").lower().endswith(".gov.au")


def append(path, cols, row):
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in cols})


def rows():
    if not os.path.exists(LOG):
        return []
    with open(LOG, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def total_bytes():
    return sum(int(r["bytes"] or 0) for r in rows() if r["status"] == "downloaded")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--region-id", required=True)
    p.add_argument("--council", required=True)
    p.add_argument("--fy", required=True, help="e.g. 2019-20 (year ended 30 June 2020)")
    p.add_argument("--url", required=True)
    p.add_argument("--source-page", required=True, help="official page where the link was found")
    p.add_argument("--title", required=True)
    p.add_argument("--doc-kind", default="gpfs")
    a = p.parse_args()
    if not re.fullmatch(r"20\d\d-\d\d", a.fy):
        sys.exit("fy must look like 2019-20")
    today = datetime.date.today().isoformat()
    base = dict(region_id=a.region_id, council=a.council, fy=a.fy, doc_kind=a.doc_kind, title=a.title,
                url=a.url, source_page=a.source_page, accessed_date=today)
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    lockf = open(LOCK, "a")

    def reject(note, code=2, status="rejected"):
        fcntl.flock(lockf, fcntl.LOCK_EX)
        append(LOG, LOG_COLS, dict(base, status=status, note=note))
        fcntl.flock(lockf, fcntl.LOCK_UN)
        print(f"{status.upper()}: {note}")
        sys.exit(code)

    host = urllib.parse.urlparse(a.url).hostname
    src_host = urllib.parse.urlparse(a.source_page).hostname
    if not official(host):
        reject(f"host {host} is not an official .gov.au host")
    if not official(src_host):
        reject(f"source page host {src_host} is not an official .gov.au host")
    for r in rows():
        if r["url"] == a.url and r["status"] in ("downloaded", "duplicate"):
            print(f"ALREADY: {r['local_path']} bytes={r['bytes']} sha256={r['sha256']}")
            sys.exit(0)
    if total_bytes() >= MAX_TOTAL:
        reject("4 GB session total already reached", code=3, status="budget_stop")

    # Fetch with plain curl (its default, honest User-Agent). Python urllib is refused (403) by many council WAFs that
    # serve curl normally; this is an ordinary client, not a circumvention. Sites that refuse curl stay "failed".
    import subprocess
    fd, tmpname = tempfile.mkstemp(dir=os.path.dirname(LOCK), suffix=".part"); os.close(fd)
    cp = subprocess.run(["curl", "-sSL", "--max-redirs", "8", "--max-time", "600", "--max-filesize", str(MAX_FILE),
                         "-o", tmpname, "-w", "%{http_code} %{url_effective}", a.url], capture_output=True, text=True)
    code, _, final_url = (cp.stdout or "").strip().partition(" ")
    if cp.returncode == 63:
        os.unlink(tmpname); reject("file exceeds 40 MB (curl --max-filesize)")
    if cp.returncode != 0 or not code.startswith("2"):
        os.unlink(tmpname); reject(f"http {code or '?'} curl exit {cp.returncode} {cp.stderr.strip()[:150]}", status="failed")
    final_host = urllib.parse.urlparse(final_url).hostname
    if not official(final_host):
        os.unlink(tmpname); reject(f"redirected to non-official host {final_host}")
    n = os.path.getsize(tmpname)
    if n > MAX_FILE:
        os.unlink(tmpname); reject("file exceeds 40 MB")
    with open(tmpname, "rb") as f:
        first = f.read(8)
    if not first.startswith(b"%PDF"):
        os.unlink(tmpname); reject(f"not a PDF (starts {first!r})")
    h = hashlib.sha256()
    with open(tmpname, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)

    class _T: name = tmpname
    tmp = _T()
    sha = h.hexdigest()

    fcntl.flock(lockf, fcntl.LOCK_EX)
    try:
        if total_bytes() + n > MAX_TOTAL:
            os.unlink(tmp.name)
            append(LOG, LOG_COLS, dict(base, bytes=n, sha256=sha, status="budget_stop",
                                       note="4 GB session total would be exceeded"))
            print("BUDGET_STOP: 4 GB session total would be exceeded. Stop all downloading and report.")
            sys.exit(3)
        for r in rows():
            if r["sha256"] == sha and r["status"] == "downloaded":
                os.unlink(tmp.name)
                append(LOG, LOG_COLS, dict(base, bytes=n, sha256=sha, local_path=r["local_path"],
                                           status="duplicate", note=f"same file as {r['url']}"))
                print(f"DUPLICATE: same content as {r['local_path']}")
                sys.exit(0)
        d = os.path.join(PDF_ROOT, a.region_id)
        os.makedirs(d, exist_ok=True)
        stem = re.sub(r"[^A-Za-z0-9]+", "_", os.path.basename(urllib.parse.urlparse(a.url).path))
        stem = re.sub(r"_?pdf$", "", stem, flags=re.I)[:60].strip("_")
        dest = os.path.join(d, f"{a.region_id}_FY{a.fy}_{a.doc_kind}_{sha[:8]}_{stem or 'doc'}.pdf")
        os.replace(tmp.name, dest)
        rel = os.path.relpath(dest, ROOT)
        append(LOG, LOG_COLS, dict(base, bytes=n, sha256=sha, local_path=rel, status="downloaded"))
        append(BIB, BIB_COLS, dict(
            source_id=f"exp10Acmp_{a.region_id}_{a.fy}_{sha[:8]}", title=a.title,
            author_or_publisher=f"{a.council} Council", year="20" + a.fy[-2:], source_type="financial_statement",
            url=a.url, accessed_date=today, local_path=rel, bytes=n, sha256=sha,
            used_in="Experiment 10/A_comparison_councils",
            what_it_was_used_for=f"Audited GPFS FY {a.fy}: capital spending, grants, expenses, disaster grant lines",
            notes=f"found via {a.source_page}"))
        print(f"OK: {rel} bytes={n} sha256={sha} session_total_bytes={total_bytes()}")
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN)


if __name__ == "__main__":
    main()
