"""Hash-lock the pre-specification (PRESPEC.md) and record the state of every protected input BEFORE any Y is built.

Writes PRESPEC.lock (refuses to overwrite) and HASHES_BEFORE.txt. run_frozen_test.py refuses to run if PRESPEC.md no
longer matches the hash recorded here. Changes to the specification are made only as dated amendments (PRESPEC.md
section 12); an amendment gets its own lock file (PRESPEC_AMEND_n.lock) via lock_amendment.py.

Run: python3 lock_prespec.py
"""
import csv
import datetime
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('/Users/ray/Research/AUSSEF - Local')
WORKBOOK = Path('/Users/ray/Library/CloudStorage/OneDrive-KnoxGrammarSchool/Extracurriculars/AUSSEF/05 Data Archive/Master Workbook (read by the analysis scripts)/nsw_bushfires_2015_2025_XY.xlsx')
DUCK = MAIN / 'data/aussef.duckdb'
OUTDIR = MAIN / 'fire_event_dataset/out'
RAW = MAIN / 'fire_event_dataset/data/raw/extra_fires'
LOCK = HERE / 'PRESPEC.lock'


def sha(p, block=1 << 22):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(block), b''):
            h.update(b)
    return h.hexdigest()


def tree_hash(d):
    h = hashlib.sha256()
    for p in sorted(x for x in d.rglob('*') if x.is_file()):
        h.update(f'{p.relative_to(d)}\t{sha(p)}\n'.encode())
    return h.hexdigest()


def protected_state():
    return {'workbook': sha(WORKBOOK), 'duckdb': sha(DUCK), 'out_tree': tree_hash(OUTDIR)}


def main():
    if LOCK.exists():
        sys.exit(f'{LOCK} exists; refusing to overwrite')
    lines = [f'locked_at: {datetime.datetime.now().astimezone().isoformat(timespec="seconds")}',
             f'PRESPEC.md sha256: {sha(HERE / "PRESPEC.md")}']
    for p in sorted((HERE / 'inputs').iterdir()):
        lines.append(f'inputs/{p.name} sha256: {sha(p)}')
    # the 8 approved downloads must match their recorded hashes
    ok = True
    for r in csv.DictReader(open(RAW / 'MANIFEST.csv')):
        got = sha(RAW / r['file'])
        good = got == r['sha256']
        ok &= good
        lines.append(f'download {r["file"]} sha256: {got} matches_MANIFEST={good}')
    lines.append(f'MANIFEST.csv sha256: {sha(RAW / "MANIFEST.csv")}')
    st = protected_state()
    (HERE / 'HASHES_BEFORE.txt').write_text('\n'.join(f'{k}: {v}' for k, v in st.items()) + '\n' +
                                            f'workbook_path: {WORKBOOK}\n')
    lines += [f'protected {k} sha256: {v}' for k, v in st.items()]
    if not ok:
        sys.exit('a download does not match MANIFEST.csv; not locking')
    LOCK.write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
