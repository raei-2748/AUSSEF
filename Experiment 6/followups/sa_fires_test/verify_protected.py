"""Recompute the SHA-256 of the master workbook, data/aussef.duckdb and the fire_event_dataset/out tree; compare with HASHES_BEFORE.txt; write HASHES_AFTER.txt."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lock_prespec import HERE, WORKBOOK, protected_state  # noqa: E402

before = dict(l.split(': ', 1) for l in (HERE / 'HASHES_BEFORE.txt').read_text().splitlines() if l.split(': ', 1)[0] in ('workbook', 'duckdb', 'out_tree'))
after = protected_state()
lines = []
for k in ('workbook', 'duckdb', 'out_tree'):
    lines.append(f'{k} before: {before[k]}')
    lines.append(f'{k} after:  {after[k]}')
    lines.append(f'{k} match:  {before[k] == after[k]}')
(HERE / 'HASHES_AFTER.txt').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
