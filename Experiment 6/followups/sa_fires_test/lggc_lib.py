"""Parser for SA Local Government Grants Commission 'Database Reports' PDFs (web-archive originals, MANIFEST p2_sa_lggc).
Rows are anchored on the council-name cell (non-numeric text left of the first numeric column); numeric cells are assigned to the
nearest row anchor by y (tolerance 3.5 pt) and to a column by their RIGHT edge (numbers are right-aligned), so blank cells do not
shift later cells. Column names come from the report list on the first page of each PDF (report_columns) and the number of x-clusters
per page must equal the number of names (asserted in check).
"""
import collections
import pickle
import re
from pathlib import Path

import numpy as np
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer, LTTextLine

RAW = Path('/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/raw/extra_fires/p2_sa_lggc')
CACHE = Path('/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/extra_fires/lggc_txt')
FILES = {2013: 'database_reports_2013-14.pdf', 2014: 'database_reports_2014-15.pdf', 2015: 'database_reports_2015-16.pdf',
         2016: 'database_reports_2016-17.pdf', 2018: 'database_reports_2018-19.pdf', 2019: 'database_reports_2019-20.pdf',
         2020: 'Database_Reports_2020-21.pdf'}
NUM = re.compile(r'^\(?-?[\d,]+(\.\d+)?\)?%?$|^-%?$|^n/?a$', re.I)


def to_num(s):
    s = s.strip()
    pct = s.endswith('%')
    s = s.replace('%', '')
    if s in ('-', '') or s.lower() in ('n/a', 'na'):
        return float('nan')
    neg = (s.startswith('(') and s.endswith(')')) or s.startswith('-')
    s = s.strip('()-').replace(',', '')
    try:
        v = float(s)
    except ValueError:
        return float('nan')
    return -v if neg else v


def raw_pages(fy):
    """[(report no, [(y0, x0, x1, text)])] for the landscape data pages; cached as a pickle (pdfminer is slow)."""
    pk = CACHE / f'pages_{fy}.pkl'
    if pk.exists():
        return pickle.load(open(pk, 'rb'))
    out = []
    for page in extract_pages(str(RAW / FILES[fy]), laparams=LAParams(line_margin=0.05, char_margin=1.0)):
        lines = []
        for el in page:
            if isinstance(el, LTTextContainer):
                for ln in el:
                    if isinstance(ln, LTTextLine):
                        t = ln.get_text().strip()
                        if t:
                            lines.append((ln.y0, ln.x0, ln.x1, t))
        title = [t for _, _, _, t in lines if re.match(r'Report \d+ ?[-–]', t)]
        m = re.match(r'Report (\d+)', title[0]) if title else None
        out.append((int(m.group(1)) if m else None, page.width > page.height, lines))
    pickle.dump(out, open(pk, 'wb'))
    return out


def table_of(lines, tol_x=6.0):
    """Return (names, cells): cells[i] = {col cluster index: value} for row i; and the column x1 centres."""
    num = [(y, x0, x1, t) for y, x0, x1, t in lines if NUM.match(t)]
    txt = [(y, x0, x1, t) for y, x0, x1, t in lines if not NUM.match(t)]
    if not num:
        return [], [], []
    # data region: numeric cells sit right of the name column
    first_x = np.percentile([x0 for _, x0, _, _ in num], 2)
    # a council-name cell: non-numeric, left of the numeric block, vertically inside the numeric cells' range
    ys = [y for y, *_ in num]
    ymin, ymax = min(ys) - 4, max(ys) + 4
    names = [(y, t) for y, x0, x1, t in txt if x1 <= first_x + 1 and ymin <= y <= ymax and not t.lower().startswith(('state total', 'page', 'source', 'notes'))]
    names = [(y, t) for y, t in names if not re.match(r'^\d+\.', t)]
    names.sort(reverse=True)
    if not names:
        return [], [], []
    anchors = np.array([y for y, _ in names])
    x1s = np.array(sorted(x1 for _, _, x1, _ in num))
    centres = []
    for x in x1s:
        if not centres or x - centres[-1][-1] > tol_x:
            centres.append([x])
        else:
            centres[-1].append(x)
    centres = [float(np.median(c)) for c in centres]
    rows = [dict() for _ in names]
    for y, x0, x1, t in num:
        i = int(np.argmin(np.abs(anchors - y)))
        if abs(anchors[i] - y) > 3.5:
            continue
        j = int(np.argmin([abs(x1 - c) for c in centres]))
        rows[i][j] = to_num(t)
    return [t for _, t in names], rows, centres


def read_reports(fy):
    """{report: {council: {col index: value}}} plus {report: number of column clusters per page}."""
    rep = collections.defaultdict(dict)
    ncols = collections.defaultdict(list)
    for rn, landscape, lines in raw_pages(fy):
        if rn is None or not landscape:
            continue
        names, rows, centres = table_of(lines)
        ncols[rn].append(len(centres))
        for n, r in zip(names, rows):
            rep[rn][n] = r
    return rep, ncols


def report_columns(fy):
    """Column names per report from the first-page list (semicolon separated, wrapped over lines)."""
    txt = (CACHE / (FILES[fy][:-4] + '.txt')).read_text()
    head = txt.split('Report 1 - General Information By Council')[0]
    blocks = re.split(r'\n\s*Report (\d+)\s*\n', head)
    out = {}
    for i in range(1, len(blocks) - 1, 2):
        body = blocks[i + 1].replace('\n', ' ')
        body = re.sub(r'\s+', ' ', body).strip()
        parts = [p.strip() for p in body.split(';')]
        out[int(blocks[i])] = parts
    return out


def col_labels(fy, rn):
    """{column cluster index: header text} for report rn (header tokens above the first council row, nearest cluster)."""
    for r, land, lines in raw_pages(fy):
        if r == rn and land:
            names, rows, cen = table_of(lines)
            top = max(y for y, x0, x1, t in lines if t.startswith('Report'))
            first = max(y for y, x0, x1, t in lines if t == names[0])
            hdr = [(y, x0, x1, t) for y, x0, x1, t in lines if first + 3 < y < top - 8 and x0 > 100 and not NUM.match(t)]
            lab = collections.defaultdict(list)
            for y, x0, x1, t in hdr:
                j = min(range(len(cen)), key=lambda k: abs((x0 + x1) / 2 - (cen[k] - 12)))
                lab[j].append((-round(y), t))
            return {j: ' '.join(t for _, t in sorted(v)) for j, v in lab.items()}, len(cen)
    raise KeyError((fy, rn))


def find_col(labels, pattern):
    hit = [j for j, t in labels.items() if re.search(pattern, t, re.I)]
    return hit[0] if len(hit) == 1 else (None if not hit else hit)
