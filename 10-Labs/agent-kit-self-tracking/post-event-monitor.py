#!/usr/bin/env python3
"""
Post-Event Council — Monitor (Jordan, Aug 24 2026)

Standing rule: after EVERY major macro event (CPI, PPI, NFP, unemployment,
FOMC + presser, Treasury announcements), convene a post-event council ~1h
after the release to capture what ACTUALLY happened vs what was expected.

This is the MONITOR script for an agent-driven cron job. It emits a hashable
snapshot:
  - On NON-event days: STABLE output ("NO_EVENT <date>") -> the cron's
    monitor hash is unchanged -> the agent stays SILENT (no tokens, no noise).
  - On EVENT days: CHANGED output (event name + live prices) -> the monitor
    hash changes -> the agent RUNS, searches live headlines (X/Twitter +
    DDG), compares to the pre-event expectation, writes minutes to the
    Strategy Journal, and delivers the read to the treasury.

Runs at 14:30 + 20:30 UTC (covers 8:30 ET morning data + afternoon events).
"""
import json
import os
import urllib.request
from datetime import datetime, timezone

UA = "Mozilla/5.0"

CALENDAR = "/root/vaults/gentech/DeFi/agentic-calendar.json"

# Macro event keywords. Event name or type containing any of these triggers
# the post-event council.
MACRO_KEYWORDS = [
    "cpi", "ppi", "nfp", "nonfarm", "unemployment", "jobs", "fomc", "fed",
    "presser", "press conference", "bessent", "treasury", "iran", "pce",
    "gdp", "rate decision", "powell", "qra", "tga", "buyback", "bond",
]


def _get(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception:
        return None


def _events_today():
    """Return macro calendar events dated today that have ALREADY released.

    An event is only "post-event" if its release time has passed. Events with a
    `release_utc` field ("HH:MM") are gated on it; events without one are
    treated as released (back-compat). This prevents a pre-release run from
    firing a premature post-event council (bug: 2026-09-10 CPI false trigger).
    """
    if not os.path.exists(CALENDAR):
        return []
    try:
        cal = json.load(open(CALENDAR))
    except Exception:
        return []
    now = datetime.now(timezone.utc)
    today = now.date()
    matches = []
    for ev in cal.get("events", []):
        try:
            ev_date = datetime.fromisoformat(ev["date"]).date()
        except Exception:
            continue
        if ev_date != today:
            continue
        # Lifecycle gate: completed/removed events never re-fire.
        if str(ev.get("status", "")).lower() in ("done", "removed", "cancelled"):
            continue
        # Release-time gate: skip if the release hasn't happened yet today.
        rel = str(ev.get("release_utc", "")).strip()
        if rel:
            try:
                hh, mm = (int(x) for x in rel.split(":")[:2])
                if (now.hour, now.minute) < (hh, mm):
                    continue
            except Exception:
                pass
        name = ev.get("name", "").lower()
        etype = ev.get("type", "").lower()
        if any(kw in name or kw in etype for kw in MACRO_KEYWORDS):
            matches.append(ev.get("name", "Macro event"))
    return matches


def _live_prices():
    try:
        d = _get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,avalanche-2,solana,ethereum&vs_currencies=usd&include_24hr_change=true")
        if not d:
            return []
        out = []
        for k, label in [("bitcoin", "BTC"), ("avalanche-2", "AVAX"), ("solana", "SOL"), ("ethereum", "ETH")]:
            if k in d:
                out.append(f"{label} ${d[k]['usd']:,.0f} ({d[k].get('usd_24h_change', 0):+.2f}%)")
        return out
    except Exception:
        return []


def main():
    now = datetime.now(timezone.utc)
    events = _events_today()

    if not events:
        # STABLE on non-event days -> agent stays silent. No date/timestamp
        # (would change daily and trigger a needless run).
        print("NO_EVENT")
        return

    prices = _live_prices()
    print(f"MACRO_EVENT {now.date().isoformat()} {now.strftime('%H:%M')} UTC")
    for e in events:
        print(f"EVENT: {e}")
    for p in prices:
        print(f"PRICE: {p}")


if __name__ == "__main__":
    main()
