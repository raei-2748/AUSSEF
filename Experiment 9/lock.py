"""Write LOCK.txt: sha256 of the pre-spec, the config and the input files. Run before fitting anything."""
import hashlib
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import data  # noqa: E402

files = [HERE / 'PRESPEC.md', HERE / 'config.toml', data.WORKBOOK] + [data.src(k) for k in ('dl_filled', 'council_items', 'affected', 'v3') if k in data.CFG['sources']]
lines = [f'locked {time.strftime("%Y-%m-%d %H:%M:%S")}']
for f in files:
    lines.append(f'{hashlib.sha256(Path(f).read_bytes()).hexdigest()}  {Path(f).name}')
(HERE / 'LOCK.txt').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
