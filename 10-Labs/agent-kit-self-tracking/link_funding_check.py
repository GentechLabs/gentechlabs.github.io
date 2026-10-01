#!/usr/bin/env python3
"""LINK.e/USDC gauge — funding cadence + staked fraction (Sep 12 2026).

Decisive tests:
  1. Is the gauge being FUNDED? (BLACK transfers in/out over time.)
  2. How much is actually STAKED vs the pool? (Decides whether we capture most
     of the emissions or a sliver — THE number that makes or breaks this pool.)
"""
import json
import urllib.request
from datetime import datetime, timezone

GAUGE_LU = "0x014D8De7Fa79320C1750C4702b7830C3987F8B51"
GAUGE_LB = "0x8e6a5b139c8bce33241437355569AB2C50f77443"
BLACK_USD = 0.00234
RATE_PER_DAY = 117.9231


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def black_flows(gauge, label):
    url = ("https://api.snowtrace.io/api?module=account&action=tokentx"
           f"&address={gauge}&page=1&offset=200&sort=desc")
    d = get(url)
    res = [t for t in (d.get("result") or []) if t.get("tokenSymbol") == "BLACK"]
    print(f"\n── {label} — BLACK flows ──")
    print(f"   records: {len(res)}")
    seen = set()
    ins = 0
    for t in res:
        ts = int(t["timeStamp"])
        v = int(t["value"]) / 1e18
        key = (ts, t["to"].lower())
        if key in seen:
            continue
        seen.add(key)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        into = t["to"].lower() == gauge.lower()
        if into:
            ins += 1
        print(f"   {dt}  {'IN ' if into else 'OUT'} {v:>11,.4f} BLACK  (${v*BLACK_USD:,.3f})")
    return ins


def main():
    print("=" * 72)
    print("LINK GAUGES — FUNDING CADENCE")
    print("=" * 72)
    print(f"  BLACK ${BLACK_USD}   |  advertised {RATE_PER_DAY:.2f} BLACK/day")
    print(f"  7-day funding should be {RATE_PER_DAY*7:,.4f} BLACK")

    black_flows(GAUGE_LU, "LINK.e/USDC gauge")
    black_flows(GAUGE_LB, "LINK.e/BLACK gauge")


if __name__ == "__main__":
    raise SystemExit(main())
