#!/usr/bin/env python3
"""discover-news-sources.py — find and TEST sources that carry what was SAID, not just when.

Jordan (Sep 16 2026): "let's look for where we can go to track these meetings and what's
being said after. So not only do we know the days that is happening, but we also can get
the details."

We already know the DATES (agentic-calendar.json, DST-correct). We can read DOCUMENTS
(Federal Register — sec-cftc-watch.py). What we cannot yet do is read SPEECH: the statement
as issued, the press conference, the minutes, the speeches and testimony around it.

This script probes every candidate endpoint and reports what ACTUALLY answers, with an item
count and a real headline as proof. Nothing is assumed available because it "should" be.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept": "application/rss+xml, application/xml, application/json, text/html;q=0.9"}

CANDIDATES = [
    # ── Federal Reserve ──────────────────────────────────────────────────────
    ("FED press releases (all)", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("FED monetary policy", "https://www.federalreserve.gov/feeds/press_monetary.xml"),
    ("FED speeches", "https://www.federalreserve.gov/feeds/speeches.xml"),
    ("FED testimony", "https://www.federalreserve.gov/feeds/testimony.xml"),
    # ── SEC ──────────────────────────────────────────────────────────────────
    ("SEC press releases", "https://www.sec.gov/news/pressreleases.rss"),
    ("SEC speeches & statements", "https://www.sec.gov/news/speeches-statements.rss"),
    ("SEC litigation", "https://www.sec.gov/rss/litigation/litreleases.xml"),
    # ── CFTC ─────────────────────────────────────────────────────────────────
    ("CFTC press releases", "https://www.cftc.gov/RSS/RSSGP/rssgp.xml"),
    ("CFTC speeches & testimony", "https://www.cftc.gov/RSS/RSSST/rssst.xml"),
    # ── Treasury / White House ───────────────────────────────────────────────
    ("US Treasury press", "https://home.treasury.gov/rss/press.xml"),
    # ── Federal Register (we already use it — control) ────────────────────────
    ("FR: Fed system docs", "https://www.federalregister.gov/api/v1/documents.json"
                            "?conditions[agencies][]=federal-reserve-system&per_page=5"
                            "&order=newest&fields[]=title&fields[]=publication_date"),
]

TAG = re.compile(r"\{[^}]*\}")


def probe(name: str, url: str) -> dict:
    out = {"name": name, "url": url}
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            out["status"] = r.status
            body = r.read(400_000)
    except urllib.error.HTTPError as e:
        out.update(status=e.code, error=f"HTTP {e.code}")
        return out
    except Exception as e:                                           # noqa: BLE001
        out.update(status=None, error=f"{type(e).__name__}: {e}")
        return out

    out["bytes"] = len(body)
    txt = body.decode("utf-8", "replace")

    # JSON path
    if txt.lstrip().startswith(("{", "[")):
        try:
            d = json.loads(txt)
            if isinstance(d, dict) and "results" in d:
                out["kind"] = "json"
                out["items"] = d.get("count", len(d["results"]))
                rs = d.get("results") or []
                if rs:
                    out["sample"] = str(rs[0].get("title"))[:110]
                    out["sample_date"] = rs[0].get("publication_date")
                return out
        except Exception:
            pass

    # RSS/XML path
    try:
        root = ET.fromstring(body)
        items = root.findall(".//item")
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
        out["kind"] = "xml"
        out["items"] = len(items)
        if items:
            it = items[0]
            t = it.findtext("title") or ""
            if not t:
                for ch in it:
                    if TAG.sub("", ch.tag) == "title":
                        t = (ch.text or "")
                        break
            d = it.findtext("pubDate") or it.findtext("updated") or ""
            out["sample"] = t.strip()[:110]
            out["sample_date"] = d.strip()[:31]
        return out
    except Exception as e:                                           # noqa: BLE001
        out["kind"] = "unknown"
        out["error"] = f"not json/xml ({type(e).__name__})"
        out["head"] = txt[:80].replace("\n", " ")
        return out


def main() -> int:
    print("═" * 78)
    print("  NEWS / CONTENT SOURCE DISCOVERY — probed live, not assumed")
    print("═" * 78)
    live, dead = [], []
    for name, url in CANDIDATES:
        r = probe(name, url)
        if r.get("error") and not r.get("items"):
            dead.append(r)
            print(f"\n  ❌ {name}")
            print(f"       {r.get('error')}")
        else:
            live.append(r)
            print(f"\n  ✅ {name}   [{r.get('kind')} · {r.get('status')} · {r.get('bytes',0):,}B]")
            print(f"       items : {r.get('items')}   latest: {r.get('sample_date','')}")
            if r.get("sample"):
                print(f"       sample: {r['sample']}")
    print()
    print("═" * 78)
    print(f"  LIVE: {len(live)}   DEAD: {len(dead)}")
    print("═" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
