"""Check every URL cited in the two workbooks; record status and, for dead links, a Wayback Machine copy.

Writes out/link_check.csv (url, status, archive_url, verdict). Verdicts: ok; blocked (403: the site refuses automated
requests, not proven dead); dead_archived (404/410 with a Wayback copy, which is used instead); dead (no copy);
not_a_link (text instead of a URL, a bare site homepage that does not point to the item, or Wikipedia,
which is not accepted as a source).
Run: ../.venv/bin/python -m src.linkcheck
"""
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from src.common import OUT

BARE = re.compile(r"^https?://[^/]+/?$|/New-South-Wales/?$", re.I)


def status(u):
    r = subprocess.run(["curl", "-sL", "-o", "/dev/null", "-A", "Mozilla/5.0", "--max-time", "40", "-r", "0-2000",
                        "-w", "%{http_code}", u], capture_output=True, text=True)
    return r.stdout.strip() or "000"


def wayback(u):
    r = subprocess.run(["curl", "-s", "--max-time", "30", f"https://archive.org/wayback/available?url={u}"],
                       capture_output=True, text=True)
    try:
        c = json.loads(r.stdout).get("archived_snapshots", {}).get("closest")
        return c["url"].replace("http://", "https://", 1) if c and c.get("available") else ""
    except (ValueError, KeyError):
        return ""


def clean(u):
    """First URL in the text (drops trailing comments such as '(PDF p.12)' or '(background only)')."""
    m = re.search(r"https?://\S+", str(u))
    if not m:
        return str(u).strip()
    u = m.group().rstrip(".,;")
    while u.endswith(")") and u.count(")") > u.count("("):  # a closing bracket of a trailing comment, not the URL
        u = u[:-1]
    return u


def check(urls):
    urls = sorted({clean(u) for u in urls if isinstance(u, str) and u.strip()})
    def one(u):
        if not re.match(r"^https?://\S+$", u) or BARE.search(u) or "{" in u or "wikipedia.org" in u:
            return dict(url=u, status="", archive_url="", verdict="not_a_link")
        s = status(u)
        if s in ("200", "206"):
            return dict(url=u, status=s, archive_url="", verdict="ok")
        if s == "403":
            return dict(url=u, status=s, archive_url=wayback(u), verdict="blocked")
        a = wayback(u)
        return dict(url=u, status=s, archive_url=a, verdict="dead_archived" if a else "dead")
    with ThreadPoolExecutor(12) as ex:
        res = pd.DataFrame(list(ex.map(one, urls)))
    res.to_csv(OUT / "link_check.csv", index=False)
    return res


def load():
    p = OUT / "link_check.csv"
    return pd.read_csv(p, dtype=str).fillna("") if p.exists() else pd.DataFrame(columns=["url", "verdict", "archive_url"])


if __name__ == "__main__":
    import glob
    from src.links import rows
    urls = list(rows().download_url)
    for p in glob.glob(str(OUT.parent / "data/key_events/*.csv")):
        d = pd.read_csv(p, dtype=str)
        for c in ("source_url", "key_sources", "decl_source_url"):
            if c in d:
                for v in d[c].dropna():
                    urls += re.split(r"\s*[;|]\s*|\s+(?=https?://)", v)
    from src import socio
    from src.key_events import LOCAL_COPIES
    urls += list(socio.disasters().decl_source_url.dropna()) + list(LOCAL_COPIES.values())
    corr = OUT.parent / "data/key_events/corrections.csv"
    if corr.exists():
        c = pd.read_csv(corr, dtype=str)
        urls += list(c.loc[c.action == "set_source", "new_value"].dropna())
    r = check(urls)
    print(r.verdict.value_counts().to_dict())
    print(r[r.verdict != "ok"].to_string())
