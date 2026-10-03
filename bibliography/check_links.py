"""Check every URL in BIBLIOGRAPHY.csv and record the result.

Run:  python3 bibliography/check_links.py [--recheck-days N]

- Tests each row's check_url (its url, or https://doi.org/<doi> when only a DOI is given).
- HEAD first, then GET (streamed, body not downloaded) when HEAD is refused or fails.
- Normal browser User-Agent; polite: at most one request per host every 2 s, 6 hosts in parallel.
- Results go to link_status.csv (url, link_status, http_code, final_url, checked_date), then
  merge_bibliography.py is re-run so BIBLIOGRAPHY.csv/.xlsx carry the link_status column.
- URLs checked within --recheck-days (default 7) are not re-requested.

link_status values:
  OK            2xx (after redirects)
  BLOCKED       401/403/429 - site refuses automated requests; usually fine in a browser, check by hand
  BROKEN        404/410 or other 4xx
  SERVER ERROR  5xx
  REDIRECT      3xx left unresolved (e.g. redirect to a login page); check by hand
  FAILED        DNS/connection/timeout/SSL error
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import subprocess
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit

import requests

HERE = Path(__file__).resolve().parent
BIB = HERE / 'BIBLIOGRAPHY.csv'
LINK_STATUS = HERE / 'link_status.csv'
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/128.0 Safari/537.36')
HEADERS = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/pdf,*/*;q=0.8',
           'Accept-Language': 'en-AU,en;q=0.9'}
PER_HOST_GAP = 2.0
TIMEOUT = 25
FIELDS = ['url', 'link_status', 'http_code', 'final_url', 'checked_date', 'error']

_host_locks: dict[str, threading.Lock] = defaultdict(threading.Lock)
_host_last: dict[str, float] = {}


def classify(code: int) -> str:
    if 200 <= code < 300:
        return 'OK'
    if code in (401, 403, 429):
        return 'BLOCKED'
    if 400 <= code < 500:
        return 'BROKEN'
    if code >= 500:
        return 'SERVER ERROR'
    if 300 <= code < 400:
        return 'REDIRECT'
    return f'HTTP {code}'


def check(url: str) -> dict:
    today = dt.date.today().isoformat()
    host = urlsplit(url).netloc.lower()
    with _host_locks[host]:          # one request at a time per host, spaced PER_HOST_GAP apart
        res = {'url': url, 'checked_date': today, 'http_code': '', 'final_url': '', 'error': ''}
        try:
            for method in ('HEAD', 'GET'):
                wait = PER_HOST_GAP - (time.monotonic() - _host_last.get(host, 0))
                if wait > 0:
                    time.sleep(wait)
                _host_last[host] = time.monotonic()
                try:
                    r = requests.request(method, url, headers=HEADERS, timeout=TIMEOUT,
                                         allow_redirects=True, stream=True)
                    r.close()
                except requests.RequestException as e:
                    if method == 'GET':
                        raise
                    res['error'] = f'HEAD: {type(e).__name__}'
                    continue
                res['http_code'] = str(r.status_code)
                res['final_url'] = r.url if r.url != url else ''
                if 200 <= r.status_code < 300:
                    break
            res['link_status'] = classify(int(res['http_code']))
        except requests.RequestException as e:
            res['link_status'] = 'FAILED'
            res['error'] = f'{type(e).__name__}: {str(e)[:150]}'
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--recheck-days', type=int, default=7)
    a = ap.parse_args()
    if not BIB.exists():
        sys.exit('run merge_bibliography.py first')
    subprocess.run([sys.executable, str(HERE / 'merge_bibliography.py')], check=True)

    with BIB.open(newline='', encoding='utf-8') as fh:
        urls = sorted({r['check_url'] for r in csv.DictReader(fh) if r['check_url'].startswith('http')})
    old = {}
    if LINK_STATUS.exists():
        with LINK_STATUS.open(newline='', encoding='utf-8') as fh:
            old = {r['url']: r for r in csv.DictReader(fh)}
    cutoff = (dt.date.today() - dt.timedelta(days=a.recheck_days)).isoformat()
    todo = [u for u in urls if u not in old or old[u]['checked_date'] < cutoff]
    print(f'{len(urls)} URLs, {len(todo)} to check')

    results = dict(old)
    lock = threading.Lock()
    done = [0]

    def save():
        with LINK_STATUS.open('w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, FIELDS)
            w.writeheader()
            w.writerows(results[u] for u in sorted(results))

    def run(u):
        r = check(u)
        with lock:
            results[u] = r
            done[0] += 1
            if done[0] % 25 == 0:
                print(f'  {done[0]}/{len(todo)}', flush=True)
                save()

    # interleave hosts round-robin so the 6 workers spread across hosts; the per-host lock keeps it polite
    by_host = defaultdict(list)
    for u in todo:
        by_host[urlsplit(u).netloc.lower()].append(u)
    queues = sorted(by_host.values(), key=len, reverse=True)
    todo = [q[i] for i in range(max(map(len, queues), default=0)) for q in queues if i < len(q)]
    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(run, todo))
    save()

    counts = defaultdict(int)
    for u in urls:
        counts[results[u]['link_status']] += 1
    print(dict(counts))
    subprocess.run([sys.executable, str(HERE / 'merge_bibliography.py')], check=True)


if __name__ == '__main__':
    main()
