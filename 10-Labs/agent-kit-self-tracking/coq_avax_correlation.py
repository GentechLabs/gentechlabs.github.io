#!/usr/bin/env python3
"""coq_avax_correlation.py — is COQ moving WITH AVAX, or on its own?

Jordan, 2026-09-22:
    "I think you should start looking for correlations, right? Is COQ still following AVAX
     or is it decoupling AVAX... the same way that most altcoins are following Bitcoin.
     Because at some point in time Bitcoin was just kind of sitting there not doing
     anything and altcoins just started going up by themselves... I like the idea of
     correlating AVAX and COQ together because they move kind of similar, although the
     meme coin moves more harsh."

WHY THIS EXISTS
---------------
"Is COQ at a 30-day high?" is a WEAKER question than "is COQ at a 30-day high RELATIVE
TO AVAX?"

    * If AVAX is flat and COQ is +62%, that is COQ-specific froth. It usually mean-reverts,
      and buying it is buying a spike.
    * If AVAX is +40% over the same window, COQ's move is largely BETA. Buying it is buying
      the sector, not chasing a candle.

The absolute price level cannot tell those apart. Beta and R-squared can. So this script
splits COQ's return into:
    * the part EXPLAINED by AVAX   (beta x AVAX's move)
    * the part that is IDIOSYNCRATIC (residual)
and reports whether COQ is currently tracking AVAX or decoupling from it.

The BTC/alt analogue Jordan named is exactly this: alts sat still while BTC chopped, then
ran on their own. The DECOUPLING was the signal -- not the price level.

READ-ONLY. Moves no money, touches no wallet. Safe to run any time.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
import urllib.request

COQ = "coq-inu"
AVAX = "avalanche-2"


def _get(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def daily_closes(coin_id: str, days: int) -> list:
    """Daily closes, oldest first. CoinGecko returns [ms, price] pairs."""
    url = (f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
           f"?vs_currency=usd&days={days}&interval=daily")
    d = _get(url)
    return [p[1] for p in d.get("prices") or []]


def log_returns(prices: list) -> list:
    """Log returns. Log, not simple, so a +50% then -50% does not cancel to zero."""
    out = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0 and prices[i] > 0:
            out.append(math.log(prices[i] / prices[i - 1]))
        else:
            out.append(0.0)
    return out


def pearson(a: list, b: list) -> float | None:
    n = min(len(a), len(b))
    if n < 3:
        return None
    a, b = a[-n:], b[-n:]
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((y - mb) ** 2 for y in b) ** 0.5
    if da == 0 or db == 0:
        return None
    return num / (da * db)


def beta(asset: list, bench: list) -> float | None:
    """asset's sensitivity to bench: cov(a,b) / var(b)."""
    n = min(len(asset), len(bench))
    if n < 3:
        return None
    a, b = asset[-n:], bench[-n:]
    ma, mb = statistics.mean(a), statistics.mean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (n - 1)
    varb = sum((y - mb) ** 2 for y in b) / (n - 1)
    if varb == 0:
        return None
    return cov / varb


def main(argv: list) -> int:
    days = 90
    if "--days" in argv:
        try:
            days = int(argv[argv.index("--days") + 1])
        except Exception:
            pass

    try:
        coq = daily_closes(COQ, days)
        avax = daily_closes(AVAX, days)
    except Exception as e:
        print(f"  ❌ price fetch failed: {type(e).__name__}: {str(e)[:80]}")
        return 1

    n = min(len(coq), len(avax))
    coq, avax = coq[-n:], avax[-n:]
    if n < 8:
        print(f"  ❌ not enough history ({n} points)")
        return 1

    cr, ar = log_returns(coq), log_returns(avax)

    print("=" * 74)
    print("  COQ vs AVAX — is COQ following, or decoupling?")
    print("=" * 74)
    print(f"  window: {n} daily closes  |  COQ ${coq[-1]:.10f}  |  AVAX ${avax[-1]:,.2f}")
    print()

    for label, span in (("7d", 7), ("30d", 30), (f"{n}d (full)", n)):
        k = min(span, len(cr))
        if k < 3:
            continue
        c_slice, a_slice = cr[-k:], ar[-k:]
        r = pearson(c_slice, a_slice)
        b = beta(c_slice, a_slice)
        coq_ret = (coq[-1] / coq[-1 - k] - 1) * 100
        avax_ret = (avax[-1] / avax[-1 - k] - 1) * 100
        print(f"  {label}")
        print(f"    COQ  {coq_ret:+7.1f}%      AVAX {avax_ret:+7.1f}%")
        if r is not None:
            r2 = r * r
            print(f"    correlation {r:+.2f}    R² {r2:.2f}  "
                  f"({r2*100:.0f}% of COQ's move explained by AVAX)")
        if b is not None:
            explained = b * avax_ret
            resid = coq_ret - explained
            print(f"    beta        {b:+.2f}   (COQ moves {b:.2f}x AVAX)")
            print(f"    explained   {explained:+7.1f}%  by AVAX")
            print(f"    residual    {resid:+7.1f}%  COQ-specific")
        print()

    # ── the verdict Jordan actually wants ────────────────────────────────────────
    k = min(7, len(cr))
    r7 = pearson(cr[-k:], ar[-k:])
    b7 = beta(cr[-k:], ar[-k:])
    coq7 = (coq[-1] / coq[-1 - k] - 1) * 100
    avax7 = (avax[-1] / avax[-1 - k] - 1) * 100
    resid7 = coq7 - (b7 * avax7 if b7 is not None else 0)

    print("─" * 74)
    print("  READ")
    print("─" * 74)
    if r7 is not None and r7 < 0.35:
        print(f"  DECOUPLED (7d corr {r7:+.2f}). COQ is not tracking AVAX right now.")
        if resid7 > 5:
            print(f"  And its move is mostly its own: {resid7:+.1f}% idiosyncratic over 7d.")
            print("  → This is the froth case. A pullback here is more likely than a continuation.")
        elif resid7 < -5:
            print(f"  COQ is WEAK vs its own beta: {resid7:+.1f}% residual over 7d.")
            print("  → Relative weakness while decoupled — the better entry setup.")
    elif r7 is not None and r7 > 0.65:
        print(f"  TRACKING (7d corr {r7:+.2f}). COQ is moving with AVAX.")
        print("  → A COQ dip that is just AVAX dipping is a SECTOR entry, not a COQ call.")
        print("    Judge it on AVAX's chart, and on whether you want AVAX here.")
    else:
        print(f"  MIXED (7d corr {r7:+.2f}). Partial coupling — neither clean read.")
        print(f"  COQ 7d {coq7:+.1f}%, AVAX 7d {avax7:+.1f}%, residual {resid7:+.1f}%.")
    print()
    print("  NOTE: correlation is not a rule. It is context for the dip trigger — a COQ dip")
    print("  that is AVAX-wide is a different decision from a COQ dip that is COQ-only.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
