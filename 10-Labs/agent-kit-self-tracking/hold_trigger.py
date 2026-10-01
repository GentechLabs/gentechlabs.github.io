#!/usr/bin/env python3
"""hold_trigger.py — when should the treasury actually HOLD instead of farm?

Jordan (2026-09-17), defining the discipline:

  "we don't want to say oh, we're bullish and we're going up when we're normally just steady.
   our bullish mode is going to be when we see moves like 10 basis points, 10 basis points
   plus type of moves, because any other thing we could just be yield farming and market
   making and be fine. So ... we'd have to look and say okay, we've been bullish on the
   monthly and the weekly, now we should consider holding. It depends on how much we're
   making versus fee generation for the yield mode."

That decomposes into three gates, and ALL THREE must pass:

  GATE 1 — BOTH TIMEFRAMES. Monthly AND weekly must be bullish. One alone is noise; he said
           "we've been bullish on the monthly and the weekly".
  GATE 2 — REAL MOVEMENT, NOT DRIFT. He is explicit that 'steady' is not a reason to hold:
           "we don't want to say we're bullish ... when we're normally just steady". So the
           trend must show actual directional days, not a flat line with a positive slope.
  GATE 3 — OPPORTUNITY COST. Holding forfeits the fee core. "It depends on how much we're
           making versus fee generation." Holding wins only if the expected move beats the
           fees given up. We already measured our fee core at 45-49% APR, so this gate is
           the binding one almost always — which is the point.

THE DEFAULT IS FARM. This script exists to say NO. A gate that opens easily is not a gate,
and the whole design premise is that chop is our preferred weather.

── ONE AUTHORITY (2026-09-26) ─────────────────────────────────────────────────────────────
`evaluate(pts)` is the ONLY implementation of the three gates. `main()` prints it as prose
and `--json` emits the same structure, so a caller never has to regex prose to learn the
verdict. momentum_watch.py imports `evaluate` rather than re-deriving the gates: two copies
of a gate are two gates that will disagree, and the copy that disagrees quietly is the one
that gets trusted.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

FEE_APR = 0.47          # our measured durable fee core (Black Hole CL, 7d window)
HOLD_HORIZON_D = 30     # the window a hold decision is made over
BACKTEST_D = 400        # daily history pulled for the timeframe reads


def fetch(url: str, tries: int = 5):
    last: Exception = RuntimeError("no attempt")
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=45))
        except Exception as e:                                        # noqa: BLE001
            last = e
            time.sleep(2.5 * (i + 1))
    raise last


def ols_slope(vals):
    """Least-squares slope per day on log price — a trend with drift removed."""
    import math
    n = len(vals)
    xs = list(range(n))
    ys = [math.log(v) for v in vals]
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((xs[i] - mx) ** 2 for i in range(n))
    return num / den if den else 0.0


def fetch_series():
    """Daily price series with the fallback chain. Returns (pts, source) or (None, why)."""
    try:
        d = fetch("https://api.coingecko.com/api/v3/coins/avalanche-2/market_chart"
                  f"?vs_currency=usd&days={BACKTEST_D}&interval=daily")
        return [p for _, p in d["prices"]], "coingecko"
    except Exception:                                                 # noqa: BLE001
        # CoinGecko rate-limits bursts hard. DeFiLlama's chart endpoint carries the same
        # daily series and is more forgiving, so the gate still runs rather than going
        # dark — an unreachable feed must not read as "no signal".
        try:
            d = fetch("https://coins.llama.fi/chart/coingecko:avalanche-2"
                      "?span=400&period=1d")
            return ([p["price"] for p in
                     d["coins"]["coingecko:avalanche-2"]["prices"]], "defillama")
        except Exception as e:                                        # noqa: BLE001
            return None, f"feed unavailable on both sources: {type(e).__name__}"


def evaluate(pts) -> dict:
    """THE three gates. Structure out, no printing, no side effects.

    An unreadable series returns verdict UNKNOWN, never a silent FARM — "could not measure"
    and "no signal" are different answers with opposite actions.
    """
    if not pts or len(pts) < 60:
        return {"verdict": "UNKNOWN",
                "reason": f"insufficient history ({len(pts) if pts else 0} points)"}

    out: dict = {"spot": pts[-1]}

    # ── GATE 1: both timeframes ────────────────────────────────────────────
    results = {}
    for label, window in (("monthly", 30), ("weekly", 7)):
        if len(pts) <= window:
            continue
        seg = pts[-(window + 1):]
        chg = (seg[-1] / seg[0] - 1) * 100
        sl = ols_slope(seg)
        up = chg > 0 and sl > 0
        results[label] = {"chg": chg, "slope": sl, "up": up}
    out["timeframes"] = results
    g1 = bool(results) and all(v["up"] for v in results.values())

    # ── GATE 2: real movement, not drift ───────────────────────────────────
    # Jordan: "we don't want to say we're bullish and we're going up when we're normally
    # just steady". Steady = a positive slope carried by tiny daily changes. Real movement
    # = a majority of days moving a meaningful amount in the trend direction.
    last30 = pts[-31:]
    moves = [(last30[i] / last30[i - 1] - 1) for i in range(1, len(last30))]
    up_days = sum(1 for m in moves if m > 0)
    strong_up = sum(1 for m in moves if m >= 0.0010)     # >= +10 bps
    strong_dn = sum(1 for m in moves if m <= -0.0010)
    avg_move = sum(abs(m) for m in moves) / len(moves)
    net = (last30[-1] / last30[0] - 1)
    out.update({"up_days": up_days, "n_days": len(moves), "strong_up": strong_up,
                "strong_dn": strong_dn, "avg_move": avg_move, "net_30d": net})
    # a real trend needs more strong up days than strong down days, and a directional net
    g2 = strong_up > strong_dn and net > 0.02

    # ── GATE 3: opportunity cost ───────────────────────────────────────────
    fee_forgone = FEE_APR * HOLD_HORIZON_D / 365
    # expected move: extrapolate the monthly slope forward over the horizon, then HALVE it,
    # because extrapolating a 30d trend 30d out is optimistic and a gate should not be fed
    # its own best case.
    m_slope = results.get("monthly", {}).get("slope", 0.0)
    exp_raw = (2.718281828 ** (m_slope * HOLD_HORIZON_D)) - 1
    exp_haircut = exp_raw * 0.5
    out.update({"fee_forgone": fee_forgone, "exp_raw": exp_raw, "exp_haircut": exp_haircut})
    g3 = exp_haircut > fee_forgone

    out.update({"g1": bool(g1), "g2": bool(g2), "g3": bool(g3),
                "passed": int(g1) + int(g2) + int(g3)})
    out["verdict"] = "HOLD" if (g1 and g2 and g3) else "FARM"
    return out


def main() -> int:
    js = "--json" in sys.argv

    if not js:
        print("=" * 86)
        print(f"  HOLD TRIGGER — should we hold instead of farm?   {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
        print("=" * 86)
        print(f"  asset: AVAX   fee core forgone by holding: {FEE_APR*100:.0f}% APR")
        print(f"  decision window: {HOLD_HORIZON_D} days")
        print(f"  DEFAULT = FARM. All three gates must pass to hold.")

    pts, src = fetch_series()
    if pts is None:
        if js:
            print(json.dumps({"verdict": "UNKNOWN", "reason": src}, indent=2))
        else:
            print(f"\n  {src}")
        return 1

    if not js:
        print(f"  source: {src}  ({len(pts)} daily points)")

    ev = evaluate(pts)
    if ev["verdict"] == "UNKNOWN":
        if js:
            print(json.dumps(ev, indent=2))
        else:
            print(f"\n  {ev['reason']}")
        return 0

    if js:
        ev["source"] = src
        ev["points"] = len(pts)
        print(json.dumps(ev, indent=2))
        return 0

    tm = ev["timeframes"]
    print("\n── GATE 1 — both timeframes bullish? ──")
    for label, nice in (("monthly", "monthly (~30d)"), ("weekly", "weekly (~7d)")):
        v = tm.get(label)
        if not v:
            continue
        print(f"   {nice:<16} {v['chg']:+7.2f}%   slope/day {v['slope']*100:+6.3f}%   "
              f"{'BULLISH ✅' if v['up'] else 'not bullish ❌'}")
    print(f"   -> GATE 1: {'PASS' if ev['g1'] else 'FAIL'}")

    print("\n── GATE 2 — real directional days, not steady drift? ──")
    print(f"   30d: {ev['up_days']}/{ev['n_days']} days up")
    print(f"   days >= +10bps: {ev['strong_up']}   days <= -10bps: {ev['strong_dn']}")
    print(f"   avg |daily move|: {ev['avg_move']*100:.3f}%   net 30d: {ev['net_30d']*100:+.2f}%")
    print(f"   -> GATE 2: {'PASS' if ev['g2'] else 'FAIL'}"
          + ("" if ev["g2"] else "  (this is the 'just steady' case Jordan named)"))

    print("\n── GATE 3 — does holding beat the fee income given up? ──")
    print(f"   fee core forgone over {HOLD_HORIZON_D}d : {ev['fee_forgone']*100:.2f}%")
    print(f"   projected move (raw slope)          : {ev['exp_raw']*100:+.2f}%")
    print(f"   projected move (50% haircut)        : {ev['exp_haircut']*100:+.2f}%")
    print(f"   -> GATE 3: {'PASS' if ev['g3'] else 'FAIL'}"
          + ("" if ev["g3"] else "  (fees beat the expected move — farming wins)"))

    print("\n" + "=" * 86)
    if ev["verdict"] == "HOLD":
        print(f"  🔶 VERDICT: **HOLD is justified** — all 3 gates passed.")
        print(f"     Enter via exit mode HOLD_TOKEN (consolidate into AVAX).")
        print(f"     Log the mode change with trigger + thesis, per treasury_state.py.")
    else:
        print(f"  🟢 VERDICT: **FARM** — {ev['passed']}/3 gates passed. Default holds.")
        if not ev["g1"]:
            print("     • Both timeframes are not bullish. One alone is noise.")
        if not ev["g2"]:
            print("     • Movement is 'steady', not trending — exactly the case Jordan said")
            print("       is NOT a reason to hold: 'any other thing we could just be yield")
            print("       farming ... and be fine'.")
        if not ev["g3"]:
            print(f"     • The fee core ({FEE_APR*100:.0f}% APR) beats the expected move even")
            print("       before the haircut. Chop pays us more than a drift would.")
    print("=" * 86)
    return 0


if __name__ == "__main__":
    sys.exit(main())
