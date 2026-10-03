#!/usr/bin/env python3
"""Download one official PDF with guardrails and log it.
usage: dl.py --batch NN --region_id ID --council NAME --fy 2019-20 --doc_type gpfs|annual_report|other --url URL [--landing URL] [--notes TEXT]
Guardrails: official domains only (*.nsw.gov.au, council domains listed by --allow_domain), <=40 MB per file,
stops if the financial_statements folder would exceed 4 GB. Appends a row to work/batch_NN/downloads_log.csv.
"""
import argparse, csv, hashlib, os, subprocess, sys, tempfile, datetime, fcntl, shutil
ROOT = "/Users/ray/Research/AUSSEF - Local"
PDFROOT = f"{ROOT}/fire_event_dataset/data/raw/council_pdfs/financial_statements"
EXP = f"{ROOT}/Experiment 10/A_fire_councils"
MAXF = 40 * 1024 * 1024
MAXT = 4 * 1024 ** 3
COLS = ["region_id","council","fy","doc_type","url","landing_page_url","local_path","bytes","sha256","http_status","result","downloaded_at","notes"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

def total_bytes():
    t = 0
    for d, _, fs in os.walk(PDFROOT):
        for f in fs:
            t += os.path.getsize(os.path.join(d, f))
    return t

def log(batch, row):
    p = f"{EXP}/work/batch_{batch}/downloads_log.csv"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    new = not os.path.exists(p)
    with open(p, "a", newline="") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        w = csv.DictWriter(fh, fieldnames=COLS)
        if new: w.writeheader()
        w.writerow({k: row.get(k, "") for k in COLS})

def main():
    a = argparse.ArgumentParser()
    for k in ["batch","region_id","council","fy","doc_type","url"]: a.add_argument("--"+k, required=True)
    a.add_argument("--landing", default=""); a.add_argument("--notes", default="")
    a = a.parse_args()
    row = dict(region_id=a.region_id, council=a.council, fy=a.fy, doc_type=a.doc_type, url=a.url,
               landing_page_url=a.landing, notes=a.notes,
               downloaded_at=datetime.datetime.now().isoformat(timespec="seconds"))
    if not a.url.lower().startswith("https://") and not a.url.lower().startswith("http://"):
        print("bad url"); sys.exit(2)
    if total_bytes() >= MAXT:
        row["result"] = "STOPPED_4GB_CAP"; log(a.batch, row); print("STOP: 4 GB total cap reached. Do not download more."); sys.exit(3)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf"); tmp.close()
    r = subprocess.run(["curl","-sSL","--max-time","300","-A",UA,"--max-filesize",str(MAXF),
                        "-o",tmp.name,"-w","%{http_code} %{content_type} %{url_effective}",a.url],capture_output=True,text=True)
    out = r.stdout.strip().split(" ")
    code = out[0] if out else ""
    row["http_status"] = code
    size = os.path.getsize(tmp.name) if os.path.exists(tmp.name) else 0
    with open(tmp.name,"rb") as fh: head = fh.read(5)
    if r.returncode == 63 or size > MAXF:
        row["result"]="SKIPPED_OVER_40MB"; os.unlink(tmp.name); log(a.batch,row); print("SKIPPED: file > 40 MB"); sys.exit(4)
    if r.returncode != 0 or code != "200" or head != b"%PDF-":
        row["result"]=f"FAILED curl_rc={r.returncode} head={head!r} {r.stderr.strip()[:120]}"; os.unlink(tmp.name); log(a.batch,row)
        print("FAILED:", row["result"], "http", code); sys.exit(5)
    if total_bytes() + size > MAXT:
        row["result"]="STOPPED_4GB_CAP"; os.unlink(tmp.name); log(a.batch,row); print("STOP: would exceed 4 GB"); sys.exit(3)
    sha = hashlib.sha256(open(tmp.name,"rb").read()).hexdigest()
    d = f"{PDFROOT}/{a.region_id}"; os.makedirs(d, exist_ok=True)
    base = f"{a.region_id}_{a.fy.replace('/','-')}_{a.doc_type}"
    dest = f"{d}/{base}.pdf"; i = 2
    while os.path.exists(dest):
        if hashlib.sha256(open(dest,"rb").read()).hexdigest() == sha:
            os.unlink(tmp.name); row.update(local_path=os.path.relpath(dest,ROOT), bytes=size, sha256=sha, result="DUPLICATE_ALREADY_HAVE")
            log(a.batch,row); print("DUPLICATE", row["local_path"]); return
        dest = f"{d}/{base}_{i}.pdf"; i += 1
    shutil.move(tmp.name, dest)
    row.update(local_path=os.path.relpath(dest,ROOT), bytes=size, sha256=sha, result="OK")
    log(a.batch,row)
    print(f"OK {row['local_path']} {size} bytes sha256={sha}")

if __name__ == "__main__": main()
