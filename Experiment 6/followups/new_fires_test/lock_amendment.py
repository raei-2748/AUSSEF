"""Hash-lock a dated amendment file. Usage: python3 lock_amendment.py PRESPEC_AMENDMENT_1.md  (refuses to overwrite its lock)."""
import datetime
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
f = HERE / sys.argv[1]
lock = f.with_suffix('.lock')
if lock.exists():
    sys.exit(f'{lock.name} exists; refusing to overwrite')
main_lock = (HERE / 'PRESPEC.lock').read_text()
line = [ln for ln in main_lock.splitlines() if ln.startswith('PRESPEC.md sha256')][0]
assert hashlib.sha256((HERE / 'PRESPEC.md').read_bytes()).hexdigest() in line, 'PRESPEC.md changed since its lock'
txt = [f'locked_at: {datetime.datetime.now().astimezone().isoformat(timespec="seconds")}',
       f'{f.name} sha256: {hashlib.sha256(f.read_bytes()).hexdigest()}', f'(PRESPEC.md unchanged: {line})']
lock.write_text('\n'.join(txt) + '\n')
print('\n'.join(txt))
