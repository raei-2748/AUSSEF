"""Hash-lock the Y-side inputs and the test script immediately before the single frozen run. Refuses to overwrite."""
import datetime
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
lock = HERE / 'Y.lock'
if lock.exists():
    sys.exit('Y.lock exists; refusing to overwrite')
files = ['results/Y_indicators_new_rows.csv', 'results/extra_fire_rows.csv', 'results/y_build_log.json', 'inputs_dl/dl_homes_sourced.csv',
         'inputs/master_reference_indicators.csv', 'build_y.py', 'run_frozen_test.py']
txt = [f'locked_at: {datetime.datetime.now().astimezone().isoformat(timespec="seconds")}',
       'purpose: Y-side inputs and test script frozen before the single frozen test run; the score table is locked earlier in SCORES.lock']
for f in files:
    txt.append(f'{f} sha256: {hashlib.sha256((HERE / f).read_bytes()).hexdigest()}')
lock.write_text('\n'.join(txt) + '\n')
print('\n'.join(txt))
