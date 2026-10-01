#!/usr/bin/env python3
"""stock-vs-crypto-cycle.py — do stocks and crypto bull together, or take turns?

Jordan (2026-09-18), on Ondo's "440+ tokenized assets" post: "we should look into tokenized stock
strategies and when the stock market has a bull market versus crypto."

Measurable, so measured: correlation of daily returns, rolling (a single number hides regimes), and
the DIVERGENCE windows where one ran and the other did not.

SOURCES, named per doctrine:
  equities -> api.nasdaq.com historical endpoint (free, keyless, verified working 2026-09-19)
              Yahoo 429s, Stooq serves a JS hashcash challenge, FRED returned 0 bytes.
  crypto   -> Coinbase Exchange candles (free, keyless, verified accurate)
Neither is chain truth and this file does not pretend otherwise: there is no on-chain source for the
S&P 500. Named provider tier, stated plainly. READ-ONLY.
"""
from __future__ import annotations

import json
import math
import time
import urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "application/json, text/plain, */*"}


def nasdaq(sym: str, years: int = 6) -> dict:
    """Daily closes from the Nasdaq public quote API. Handles its $ and comma formatting."""
    out = {}
    start = (datetime.now(timezone.utc) - timedelta(days=365 * years)).strftime("%Y-%m-%d")
    url = (f"https://api.nasdaq.com/api/quote/{sym}/historical"
           f"?assetclass={'etf' if sym in ('SPY', 'QQQ') else 'stocks'}"
           f"&fromdate={start}&limit=9999")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            d = json.load(r)
        rows = (d.get("data") or {}).get("tradesTable", {}).get("rows") or []
    except Exception as e:
        raise RuntimeError(f"{sym}: Nasdaq fetch failed {type(e).__name__}: {str(e)[:90]}")
    for row in rows:
        try:
            dt = datetime.strptime(row["date"], "%m/%d/%Y").strftime("%Y-%m-%d")
            out[dt] = float(str(row["close"]).replace("$", "").replace(",", ""))
        except Exception:
            continue
    return out


def coinbase(product: str, days: int = 2400) -> dict:
    raw, cur = [], datetime.now(timezone.utc) - timedelta(days=days)
    end = datetime.now(timezone.utc)
    while cur < end:
        stop = min(cur + timedelta(days=299), end)
        u = (f"https://api.exchange.coinbase.com/products/{product}/candles"
             f"?granularity=86400&start={cur.isoformat()}&end={stop.isoformat()}")
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
                raw.extend(json.load(r))
        except Exception:
            pass
        cur = stop + timedelta(days=1)
        time.sleep(0.3)
    return {datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d"): c
            for t, _l, _h, _o, c, _v in raw}


def corr(a, b):
    n = len(a)
    if n < 20:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a) / n)
    sb = math.sqrt(sum((x - mb) ** 2 for x in b) / n)
    return cov / (sa * sb) if sa and sb else None


def main():
    print("=" * 100)
    print("  STOCKS vs CRYPTO — do they bull together, or take turns?")
    print("=" * 100)

    spx = nasdaq("SPY")
    qqq = nasdaq("QQQ")
    print(f"\n  SPY (S&P 500) : {len(spx)} days   {min(spx) if spx else '-'} -> {max(spx) if spx else '-'}")
    print(f"  QQQ (Nasdaq)  : {len(qqq)} days")
    btc = coinbase("BTC-USD")
    eth = coinbase("ETH-USD")
    print(f"  BTC           : {len(btc)} days   {min(btc) if btc else '-'} -> {max(btc) if btc else '-'}")

    def rets(x, y, pivot):
        com = sorted(set(x) & set(y))
        gy = com[:len(com) - (len(com) - len(com))] if False else com
        ann = [d for d in gy if d >= pivot] if pivot else gy
        rx = [math.log(x[ann[i]] / x[ann[i - 1]]) for i in range(1, len(ann))]
        ry = [math.log(y[ann[i]] / y[ann[i - 1]]) for i in range(1, len(ann))]
        return ann, rx, ry

    com, rsp, rbt = rets(spx, btc, None)
    print(f"\n  overlapping window: {com[0]} -> {com[-1]}  ({len(com)} days)")

    print("\n" + "=" * 100)
    print("  1 ── CORRELATION OF DAILY RETURNS")
    print("=" * 100)
    print(f"    SPY  vs BTC : {corr(rsp, rbt):+.3f}   ({len(com)} days)")
    cq, rq, rbe = rets(qqq, btc, None)
    print(f"    QQQ  vs BTC : {corr(rq, rbe):+.3f}   ({len(cq)} days)")
    ce, rse, ree = rets(spx, eth, None)
    print(f"    SPY  vs ETH : {corr(rse, ree):+.3f}   ({len(ce)} days)")

    print("\n" + "=" * 100)
    print("  2 ── ROLLING 90-DAY CORRELATION — does the relationship hold?")
    print("=" * 100)
    W = 90
    # NB: len(rsp) == len(com) - 1, because returns are diffs of consecutive closes. Indexing the
    # date list by a returns index is the classic off-by-one here.
    n_r = len(rsp)
    rolls = [(com[i], corr(rsp[i - W:i], rbt[i - W:i])) for i in range(W, n_r + 1)]
    rolls = [(d, c) for d, c in rolls if c is not None]
    vals = [c for _, c in rolls]
    neg = sum(1 for v in vals if v < 0)
    weak = sum(1 for v in vals if abs(v) < 0.3)
    print(f"    windows          : {len(vals)}")
    print(f"    mean             : {sum(vals)/len(vals):+.3f}")
    print(f"    range            : {min(vals):+.3f}  to  {max(vals):+.3f}")
    print(f"    NEGATIVE windows : {neg}/{len(vals)}  ({neg/len(vals)*100:.0f}%)")
    print(f"    WEAK windows     : {weak}/{len(vals)}  (|r| < 0.3)")
    print(f"    latest ({rolls[-1][0]}): {rolls[-1][1]:+.3f}")

    print("\n" + "=" * 100)
    print("  3 ── DIVERGENCE — 90-day windows where one ran and the other did not")
    print("=" * 100)
    rows = []
    for i in range(W, n_r + 1):
        s = (spx[com[i]] / spx[com[i - W]] - 1) * 100
        b = (btc[com[i]] / btc[com[i - W]] - 1) * 100
        rows.append((com[i], s, b, s - b))
    print(f"    {'window end':<13}{'S&P 90d':>10}{'BTC 90d':>10}{'gap':>10}   reading")
    print("    " + "-" * 82)
    for d, s, b, g in sorted(sorted(rows, key=lambda r: -abs(r[3]))[:6]):
        print(f"    {d:<13}{s:>9.1f}%{b:>9.1f}%{g:>9.1f}%   "
              f"{'STOCKS LED' if g > 0 else 'CRYPTO LED'}")
    print("    " + "-" * 82)
    d, s, b, g = rows[-1]
    print(f"    {d:<13}{s:>9.1f}%{b:>9.1f}%{g:>9.1f}%   ← NOW "
          f"({'stocks leading' if g > 0 else 'crypto leading'})")

    big = [r for r in rows if abs(r[3]) > 20]
    sl = sum(1 for r in big if r[3] > 0)
    print(f"\n    windows with a >20pt gap: {len(big)}   stocks led {sl} / crypto led {len(big) - sl}")
    print("\n" + "=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
