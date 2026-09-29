"""Hash-lock the X side (rows, comparison groups, score table) BEFORE any Y is computed. Refuses to overwrite."""
import datetime
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
lock = HERE / 'SCORES.lock'
if lock.exists():
    sys.exit('SCORES.lock exists; refusing to overwrite')
files = ['results/roster.csv', 'results/event_polygons.csv', 'results/comparison_groups.csv', 'results/SCORES_new_rows.csv',
         'results/SCORE_ITEMS_new_rows.csv', 'results/score_build_log.json', 'build_rows.py', 'build_scores.py', 'nf_lib.py']
txt = [f'locked_at: {datetime.datetime.now().astimezone().isoformat(timespec="seconds")}',
       'purpose: X side frozen before any Y (income change, business change, finance change, homes destroyed) was computed for a new-fire council']
for f in files:
    txt.append(f'{f} sha256: {hashlib.sha256((HERE / f).read_bytes()).hexdigest()}')
lock.write_text('\n'.join(txt) + '\n')
print('\n'.join(txt))
