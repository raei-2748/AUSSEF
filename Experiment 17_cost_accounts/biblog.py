"""Append rows to this session's bibliography part (Ray's rule: log every source immediately).
Usage: python3 biblog.py 'id|title|author|year|type|url|doi|local_path|used_in|what_for|pages|quote|notes'"""
import csv, hashlib, os, sys, datetime
from pathlib import Path
ROOT = Path('/Users/ray/Research/AUSSEF - Local')
PART = ROOT / 'bibliography/parts/exp17_cost_accounts_2026-10-02.csv'
COLS = ['source_id', 'title', 'author_or_publisher', 'year', 'source_type', 'url', 'doi', 'accessed_date', 'local_path',
        'bytes', 'sha256', 'used_in', 'what_it_was_used_for', 'pages_or_table', 'quote_or_value', 'notes']


def add(source_id, title, author, year, stype, url='', doi='', local_path='', used_in='', what='', pages='', quote='', notes=''):
    b = sha = ''
    if local_path and (ROOT / local_path).is_file():
        p = ROOT / local_path
        b = p.stat().st_size
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
    new = not PART.exists()
    with open(PART, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if new:
            w.writerow(COLS)
        w.writerow([source_id, title, author, year, stype, url, doi, datetime.date.today().isoformat(), local_path, b, sha,
                    used_in, what, pages, quote, notes])


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        add(*arg.split('|'))
