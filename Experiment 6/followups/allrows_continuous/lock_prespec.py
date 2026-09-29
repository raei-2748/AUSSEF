"""Record a SHA-256 of each script's pre-specification header (its module docstring) and of the input file.

Run once after the headers are written and before any fit. allrows_continuous.py and sanity_check.py refuse to run
if their header no longer matches. results/PRESPEC_LOCK.txt keeps the timestamp.
"""
import datetime
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_lib import INPUT, LOCK, RES, header_hash

ROOT = Path(__file__).resolve().parent
RES.mkdir(exist_ok=True)
if LOCK.exists():
    sys.exit(f'{LOCK} exists; refusing to overwrite (delete it deliberately and log the change in FINDINGS.md)')
lines = [f'locked_at: {datetime.datetime.now().astimezone().isoformat(timespec="seconds")}', 'version: v2 (amends v1; v1 lock kept in results/PRESPEC_LOCK_v1.txt)']
v1 = RES / 'PRESPEC_LOCK_v1.txt'
if v1.exists():
    lines.append(f'v1 lock file sha256: {hashlib.sha256(v1.read_bytes()).hexdigest()}')
for f in ['allrows_continuous.py', 'sanity_check.py']:
    lines.append(f'{f} header sha256: {header_hash(ROOT / f)}')
lines.append(f'arc_lib.py sha256 (informational): {hashlib.sha256((ROOT / "arc_lib.py").read_bytes()).hexdigest()}')
LOCK.write_text('\n'.join(lines) + '\n')
(RES / 'INPUT_SHA256.txt').write_text(f'{hashlib.sha256(INPUT.read_bytes()).hexdigest()}  inputs/{INPUT.name}\n')
print('\n'.join(lines))
