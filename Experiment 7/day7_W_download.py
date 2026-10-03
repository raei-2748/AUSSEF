"""Day 7 dataset W: download DSS Benefit and Payment Recipient Demographics quarterly files (data.gov.au)
for Mar 2016 .. Jun 2025, and log each file in results/DAY7_DOWNLOADS.csv. Run: python3 day7_W_download.py"""
import csv, hashlib, json, re
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
DEST = Path('/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/raw/sa2/W')
LOG = HERE / 'results/DAY7_DOWNLOADS.csv'
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15'}
API = 'https://data.gov.au/data/api/3/action/package_show?id=dss-payment-demographic-data'
MAXB = 50 * 1024 * 1024
MON = {'march': 3, 'mar': 3, 'june': 6, 'jun': 6, 'september': 9, 'sept': 9, 'sep': 9, 'december': 12, 'dec': 12}


def period_of(name):
    m = re.search(r'(march|june|september|december)\s+(\d{4})', name.lower())
    return (int(m.group(2)), MON[m.group(1)]) if m else None


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    res = requests.get(API, headers=UA, timeout=60).json()['result']['resources']
    want = []
    for r in res:
        p = period_of(r['name'])
        if p and (2016, 3) <= p <= (2025, 6) and r['url'].lower().endswith('.xlsx'):
            want.append((p, r['name'].strip(), r['url']))
    new = not LOG.exists()
    done = set()
    if not new:
        done = {Path(row['file']).name for row in csv.DictReader(open(LOG)) if row['dataset'] == 'W'}
    with open(LOG, 'a', newline='') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(['dataset', 'file', 'url', 'bytes', 'sha256'])
        for p, name, url in sorted(want):
            fn = url.rsplit('/', 1)[1]
            out = DEST / fn
            if fn in done and out.exists():
                continue
            h = requests.head(url, headers=UA, allow_redirects=True, timeout=60)
            size = int(h.headers.get('content-length', 0) or 0)
            if size > MAXB:
                raise SystemExit(f'STOP: {url} is {size} bytes > 50 MB')
            r = requests.get(url, headers=UA, timeout=300)
            r.raise_for_status()
            if len(r.content) > MAXB:
                raise SystemExit(f'STOP: {url} > 50 MB')
            if not r.content[:2] == b'PK':
                raise SystemExit(f'STOP: {url} is not an xlsx (login page?)')
            out.write_bytes(r.content)
            w.writerow(['W', fn, url, len(r.content), hashlib.sha256(r.content).hexdigest()])
            print(p, name, fn, len(r.content))


if __name__ == '__main__':
    main()
