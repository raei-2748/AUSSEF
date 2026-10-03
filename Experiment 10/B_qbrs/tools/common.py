import csv, os, fcntl
ROOT = "/Users/ray/Research/AUSSEF - Local"
B = os.path.join(ROOT, "Experiment 10", "B_qbrs")
PDF_ROOT = os.path.join(ROOT, "fire_event_dataset", "data", "raw", "council_pdfs", "qbrs")
BIB_COLS = ["source_id","title","author_or_publisher","year","source_type","url","doi","accessed_date","local_path",
            "bytes","sha256","used_in","what_it_was_used_for","pages_or_table","quote_or_value","notes"]
DL_COLS = ["region_id","council","fy","quarter","url","found_on","local_path","bytes","sha256","status","accessed_date","notes"]

def append_row(path, cols, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        if new: w.writeheader()
        w.writerow({c: row.get(c, "") for c in cols})
        fcntl.flock(f, fcntl.LOCK_UN)

def dir_bytes(p):
    t = 0
    for dp, _, fs in os.walk(p):
        for f in fs:
            try: t += os.path.getsize(os.path.join(dp, f))
            except OSError: pass
    return t
