"""Write LOCK.txt: sha256 of PRESPEC.md, config.toml and the built inputs. Run after the build, before run_models.py."""
import hashlib
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
files = [HERE / 'PRESPEC.md', HERE / 'config.toml', HERE / 'inputs/v4_indicators.csv', HERE / 'inputs/FAR_SETS.csv',
         HERE.parent / 'Experiment 9/results/ANALYSIS_TABLE.csv', HERE / 'results/ANALYSIS_TABLE.csv']
lines = [f'locked {time.strftime("%Y-%m-%d %H:%M:%S")} (v4, post-v3; before any model is fitted)']
lines += [f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(HERE.parent)}' for f in files]
(HERE / 'LOCK.txt').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
