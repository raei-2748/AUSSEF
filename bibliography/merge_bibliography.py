"""Merge every bibliography/parts/*.csv into BIBLIOGRAPHY.csv and BIBLIOGRAPHY.xlsx.

Run from anywhere:  python3 bibliography/merge_bibliography.py

- Rows are deduplicated across parts: same URL (normalised), same DOI, or same sha256 => one row.
  When rows merge, every used_in value is kept (joined with " | "), notes are joined with "; ",
  and for other fields the longest non-empty value wins.
- Link-check results from check_links.py (link_status.csv) are joined on by URL.
- The xlsx has an 'All' sheet plus one sheet per source_type.
Parts files are only read, never modified.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import pandas as pd

HERE = Path(__file__).resolve().parent
PARTS = HERE / 'parts'
OUT_CSV = HERE / 'BIBLIOGRAPHY.csv'
OUT_XLSX = HERE / 'BIBLIOGRAPHY.xlsx'
LINK_STATUS = HERE / 'link_status.csv'

COLS = ['source_id', 'title', 'author_or_publisher', 'year', 'source_type', 'url', 'doi', 'accessed_date',
        'local_path', 'bytes', 'sha256', 'used_in', 'what_it_was_used_for', 'pages_or_table', 'quote_or_value',
        'notes']
TYPES = ['dataset', 'pdf_report', 'financial_statement', 'budget_review', 'journal_article', 'working_paper',
         'news', 'web_page', 'government_page', 'survey', 'other']
LIST_SEP = ' | '
TYPE_ALIASES = {'webpage': 'web_page', 'website': 'web_page', 'journal': 'journal_article', 'article': 'journal_article',
                'report': 'pdf_report', 'government': 'government_page', 'newspaper': 'news'}
ROOT = HERE.parent
# Files moved off the laptop (see ../MOVED_FILES.txt). Parts keep the original local_path; the merged
# output notes where the file now lives.
DRIVE_ARCHIVE = ('Google Drive: My Drive/Application Folder - Ray/Extracurriculars/AUSSEF/'
                 'Archive (moved from laptop 2026-10-02)/')
MOVED_PREFIXES = {'fire_event_dataset/data/raw/council_pdfs/qbrs/': 'council_pdfs/qbrs/',
                  'aussef raw data 23 sep.zip': 'aussef raw data 23 sep.zip'}
# Australian Community Media mastheads (Ray's rule: never use ACM sources). Rows are kept but flagged.
ACM_HOSTS = {h.strip() for h in ACM_FILE.read_text().splitlines() if h.strip() and not h.startswith('#')} if (ACM_FILE := HERE / 'acm_hosts.txt').exists() else set()


def norm_url(u: str) -> str:
    u = (u or '').strip()
    if not u or not re.match(r'^https?://', u, re.I):
        return ''
    p = urlsplit(u)
    host = p.netloc.lower()
    if host.startswith('www.'):
        host = host[4:]
    return urlunsplit(('https', host, p.path.rstrip('/'), p.query, ''))


def norm_doi(d: str) -> str:
    d = (d or '').strip().lower()
    d = re.sub(r'^(https?://)?(dx\.)?doi\.org/', '', d)
    d = re.sub(r'^doi:\s*', '', d)
    return d if d.startswith('10.') else ''


def check_url_for(url: str, doi: str) -> str:
    """The URL check_links.py tests for a row: its url, else its DOI resolver link."""
    if (url or '').lower().startswith('http'):
        return url.strip()
    d = norm_doi(doi)
    return f'https://doi.org/{d}' if d else ''


def read_parts() -> list[dict]:
    rows = []
    for f in sorted(PARTS.glob('*.csv')):
        with f.open(newline='', encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            missing = [c for c in COLS if c not in (reader.fieldnames or [])]
            if missing:
                print(f'WARNING {f.name}: missing columns {missing}', file=sys.stderr)
            for r in reader:
                row = {c: (r.get(c) or '').strip() for c in COLS}
                if not any(row.values()):
                    continue
                row['part_file'] = f.name
                rows.append(row)
    return rows


class UnionFind:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, i):
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def _unique(vals):
    out = []
    for v in vals:
        if v and v not in out:
            out.append(v)
    return out


def merge_group(group: list[dict]) -> dict:
    out = {}
    for c in COLS + ['part_file']:
        vals = [g[c] for g in group if g[c]]
        if c in ('used_in', 'part_file'):
            out[c] = LIST_SEP.join(_unique(x.strip() for v in vals for x in v.split('|')))
        elif c == 'notes':
            out[c] = '; '.join(_unique(vals))
        elif c == 'source_id':
            ids = _unique(vals)
            out[c] = ids[0] if ids else ''
            out['merged_ids'] = LIST_SEP.join(ids[1:])
        else:
            out[c] = max(vals, key=len) if vals else ''
    out['n_merged'] = len(group)
    return out


def dedupe(rows: list[dict]) -> list[dict]:
    uf = UnionFind(len(rows))
    first: dict[tuple, int] = {}
    for i, r in enumerate(rows):
        keys = []
        if u := norm_url(r['url']):
            keys.append(('url', u))
        if d := (norm_doi(r['doi']) or norm_doi(r['url'])):
            keys.append(('doi', d))
        if re.fullmatch(r'[0-9a-f]{64}', s := r['sha256'].lower()):
            keys.append(('sha', s))
        if not keys and r['title']:
            keys.append(('title', re.sub(r'\W+', ' ', r['title'].lower()).strip(), r['year']))
        for k in keys:
            if k in first:
                uf.union(first[k], i)
            else:
                first[k] = i
    groups: dict[int, list[dict]] = {}
    for i, r in enumerate(rows):
        groups.setdefault(uf.find(i), []).append(r)
    return [merge_group(g) for _, g in sorted(groups.items())]


def attach_link_status(df: pd.DataFrame) -> pd.DataFrame:
    df['check_url'] = [check_url_for(u, d) for u, d in zip(df['url'], df['doi'])]
    new = ['link_status', 'http_code', 'final_url', 'link_checked_date']
    if LINK_STATUS.exists():
        ls = pd.read_csv(LINK_STATUS, dtype=str, keep_default_na=False)
        ls = ls.drop_duplicates('url', keep='last').set_index('url')
        ls = ls.rename(columns={'checked_date': 'link_checked_date'})
        for c in new:
            df[c] = df['check_url'].map(ls[c]).fillna('')
    else:
        for c in new:
            df[c] = ''
    df.loc[df['check_url'] == '', 'link_status'] = 'NO URL'
    df.loc[(df['check_url'] != '') & (df['link_status'] == ''), 'link_status'] = 'not checked yet'
    return df


def main():
    rows = read_parts()
    if not rows:
        sys.exit('no rows found in bibliography/parts/*.csv')
    df = pd.DataFrame(dedupe(rows))
    df['source_type'] = df['source_type'].str.lower().replace(TYPE_ALIASES)
    bad = ~df['source_type'].isin(TYPES)
    if bad.any():
        print(f'WARNING {bad.sum()} rows with non-standard source_type -> "other"', file=sys.stderr)
        df.loc[bad, 'notes'] = (df.loc[bad, 'notes'] + '; original source_type='
                                + df.loc[bad, 'source_type']).str.strip('; ')
        df.loc[bad, 'source_type'] = 'other'
    df['_t'] = df['source_type'].map(TYPES.index)
    df['_title'] = df['title'].str.lower()
    df = df.sort_values(['_t', '_title']).drop(columns=['_t', '_title']).reset_index(drop=True)
    df.insert(0, 'bib_id', [f'B{i:04d}' for i in range(1, len(df) + 1)])
    df = attach_link_status(df)
    hosts = df['url'].map(lambda u: urlsplit(u).netloc.lower().removeprefix('www.') if u.startswith('http') else '')
    def moved(path):
        for old, new in MOVED_PREFIXES.items():
            if path.startswith(old) and not (ROOT / path).exists():
                return f'moved 2026-10-02 to {DRIVE_ARCHIVE}{new}{path[len(old):]}'
        return ''
    mv = df['local_path'].map(moved)
    df.loc[mv != '', 'notes'] = (df.loc[mv != '', 'notes'] + '; ' + mv[mv != '']).str.strip('; ')
    print(f'rows whose local file moved to Google Drive: {(mv != "").sum()}')
    df['acm_flag'] = hosts.isin(ACM_HOSTS).map({True: 'ACM - do not use', False: ''})

    cols = ['bib_id'] + COLS + ['acm_flag', 'link_status', 'http_code', 'final_url', 'link_checked_date', 'check_url',
                                'part_file', 'merged_ids', 'n_merged']
    df = df[cols]
    df.to_csv(OUT_CSV, index=False, encoding='utf-8')

    with pd.ExcelWriter(OUT_XLSX, engine='openpyxl') as xw:
        df.to_excel(xw, sheet_name='All', index=False)
        for t in TYPES:
            sub = df[df['source_type'] == t]
            if len(sub):
                sub.to_excel(xw, sheet_name=t, index=False)
        for ws in xw.book.worksheets:
            ws.freeze_panes = 'C2'
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                width = max(len(str(c.value or '')) for c in col[:300])
                ws.column_dimensions[col[0].column_letter].width = min(max(10, width + 2), 60)

    print(f'{len(rows)} part rows from {df["part_file"].str.split(" | ").explode().nunique()} files '
          f'-> {len(df)} unique sources')
    print(df['source_type'].value_counts().to_string())
    print(f'ACM-flagged rows: {(df["acm_flag"] != "").sum()}')
    print(f'written {OUT_CSV}, {OUT_XLSX}')


if __name__ == '__main__':
    main()
