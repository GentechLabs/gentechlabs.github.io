#!/usr/bin/env python3
"""stooq-client.py — fetch Stooq daily CSVs by solving its proof-of-work challenge.

WHY THIS EXISTS: Stooq's /q/d/l/ endpoint returns HTTP 200 with a JavaScript hashcash challenge
instead of a CSV when your browser is not verified. A naive client reads the 200, finds no data rows,
and reports "0 days" — which is indistinguishable from "this ticker has no history". That is the
false-value family again: a fetch that cannot tell a challenge page from a data file.

THE CHALLENGE (read off the page): it picks a random string c and a difficulty d, then loops n until
SHA-256(c + n) begins with d zero NIBBLES, and POSTs {c, n} to /__verify. d=4 means roughly 65k
hashes on average — pure busywork, trivial in Python, which is exactly why a JS wall is not a
security boundary. Solve it, keep the cookie, fetch the CSV.

Returns {date_str: close}. Raises on failure rather than returning an empty dict, so a caller can
never mistake "blocked" for "no data".
"""
from __future__ import annotations

import hashlib
import http.cookiejar
import re
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/125.0 Safari/537.36")


class StooqBlocked(RuntimeError):
    """Raised when Stooq serves a challenge we could not clear. Never silently returns empty."""


def _opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj


def _solve(c: str, d: int, limit: int = 40_000_000) -> int:
    """Find n such that sha256(c+n) starts with d zero nibbles."""
    target = "0" * d
    n = 0
    while n < limit:
        h = hashlib.sha256(f"{c}{n}".encode()).hexdigest()
        if h.startswith(target):
            return n
        n += 1
    raise StooqBlocked(f"no solution for difficulty {d} within {limit} attempts")


def _clear_challenge(opener, body: str, page_url: str) -> bool:
    """Detect and clear the hashcash challenge. True if a challenge was solved."""
    m_c = re.search(r'const c="([^"]+)"', body)
    m_d = re.search(r",d=(\d+)", body)
    if not (m_c and m_d):
        return False
    c, d = m_c.group(1), int(m_d.group(1))
    n = _solve(c, d)
    data = urllib.parse.urlencode({"c": c, "n": n}).encode()
    req = urllib.request.Request(
        urllib.parse.urljoin(page_url, "/__verify"), data=data,
        headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
                 "Referer": page_url})
    try:
        with opener.open(req, timeout=60) as r:
            r.read()
    except Exception:
        pass
    return True


def fetch(sym: str, retries: int = 3) -> dict:
    """Daily closes for a Stooq symbol. Raises StooqBlocked rather than returning {}."""
    url = f"https://stooq.com/q/d/l/?s={urllib.parse.quote(sym)}&i=d"
    opener, cj = _opener()
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with opener.open(req, timeout=60) as r:
                body = r.read().decode("utf-8", "replace")
        except Exception as e:
            raise StooqBlocked(f"{sym}: fetch failed {type(e).__name__}: {str(e)[:100]}")

        if body.lstrip().startswith("Date,") or ",Open," in body[:200]:
            return _parse(body)

        # not a CSV — almost certainly the challenge. Solve, then loop and re-request.
        if _clear_challenge(opener, body, url):
            continue
        raise StooqBlocked(f"{sym}: neither CSV nor a recognisable challenge "
                           f"(first 120 chars: {body[:120]!r})")
    raise StooqBlocked(f"{sym}: challenge not cleared after {retries} attempts")


def _parse(csv_text: str) -> dict:
    out = {}
    for line in csv_text.splitlines()[1:]:
        p = line.split(",")
        if len(p) < 5:
            continue
        try:
            out[p[0]] = float(p[4])
        except ValueError:
            continue
    return out


if __name__ == "__main__":
    import sys
    for s in (sys.argv[1:] or ["^spx", "^ndq", "spy.us"]):
        try:
            d = fetch(s)
            ks = sorted(d)
            print(f"  ✅ {s:<8} {len(d):>6} days   {ks[0] if ks else '-'} -> {ks[-1] if ks else '-'}"
                  f"   last close {d[ks[-1]] if ks else '-'}")
        except StooqBlocked as e:
            print(f"  ❌ {s:<8} {e}")
