"""Shared paths, hashing and a download manifest for the fire-event dataset."""
import csv
import datetime as dt
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
DATA, OUT = ROOT / "data", ROOT / "out"
W = Path("/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0")
PHASE1 = W / "dataset_phase1"
AUSSEF_DB = REPO / "data/aussef.duckdb"
CRS = 3577
START = "2015-01-01"
MANIFEST = DATA / "manifest.csv"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def record_source(name, path_or_url, local_path=None, licence="", note=""):
    """Append one line to the sources manifest (URL, local file, hash, access date)."""
    DATA.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()
    digest = sha256(local_path) if local_path and Path(local_path).exists() and Path(local_path).is_file() else ""
    with open(MANIFEST, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["name", "source", "local_path", "sha256", "accessed_utc", "licence", "note"])
        w.writerow([name, str(path_or_url), str(local_path or ""), digest,
                    dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), licence, note])
