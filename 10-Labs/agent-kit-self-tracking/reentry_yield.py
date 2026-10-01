#!/usr/bin/env python3
"""Re-entry Yield Plan — pairs the DeFi price rainbow with the farm we'd re-enter.

Jordan (Sep 15 2026): "the black health watch, that's to see when we should
re-enter. You could probably add that to the DeFi rainbow, or maybe that's what
we should do with the DeFi rainbow — pair it up with the farm that we're in, and
that way we can see how much more fees we could earn by buying at a cheaper price."

WHAT THIS ANSWERS
  There are TWO different rainbows and they answer different questions:
    - Coin PRICE rainbow  -> is this coin cheap or expensive?   (when to buy)
    - DeFi YIELD rainbow  -> are my LP bins earning?            (how to farm)
  This script PAIRS them: for each dip level on the ladder, what does re-entry
  actually get us?

THE HONEST MATH (this matters — it is NOT what it first looks like)
  Fee APR is earned on DEPLOYED CAPITAL, so deploying $100 at $7.26 and $100 at
  $6.50 earn the SAME fee APR. Buying cheaper does NOT raise your fee rate.

  What buying cheaper ACTUALLY buys you:
    1. MORE TOKENS per dollar. $100 at $6.50 = 15.38 AVAX vs 13.77 at $7.26
       (+11.7%). If price returns to $7.26 that surplus is real money.
    2. A BETTER RANGE POSITION. You are not buying the top of the band, so the
       range you set has less immediate downside — fewer forced re-centers.
    3. AN APR TAILWIND (conditional). If other LPs leave and volume holds, fee
       APR RISES for whoever stays. That is measured separately (black-health),
       not assumed here.

  So the output below reports the token-accumulation advantage and the fee income
  honestly side by side, and never claims a higher fee RATE from a lower entry.
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.
def _avax_url():
    """A last-resort provider STRING for callers that build their own request."""
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        # 2026-09-27 FIX: was `return _avax_url()` — a fallback that recursed into itself
        # and turned a degraded read into a RecursionError. Return a literal host; rpc()
        # carries the User-Agent that host requires.
        return "https://avalanche.drpc.org"

RPC = _avax_url()
POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"   # WAVAX/USDC 0.05% CL
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
OUT = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/reentry-yield-plan.json"

# AVAX dip ladder (dip-buy-plan-2026-09-13.md)
LADDER = [("now", 0.00), ("-5%", -0.05), ("-10%", -0.10),
          ("-18%", -0.18), ("-25%", -0.25)]

# rainbow bands (defi-rainbow-reading-guide.md) — price rainbow
BANDS = [("EUPHORIA", 1.5, 2.01, "🔴 take profits"),
         ("PEAK YIELD", 0.8, 1.5, "🟠 trim into strength"),
         ("HARVEST", 0.3, 0.8, "🟡 hold / compound"),
         ("ACCUMULATION", -0.3, 0.3, "🟢 DCA in"),
         ("BLEEDING", -0.8, -0.3, "🔵 micro-DCA / prep"),
         ("PANIC", -2.01, -0.8, "🟣 be greedy")]


def rpc(method, params, tries=1):
    """JSON-RPC to the AVAX C-Chain, carrying the User-Agent the public hosts require.

    2026-09-27 FIX — the same defect as black_health.py: Content-Type and NO
    User-Agent. publicnode (the host avax_rpc.url() returns) answers a bare urllib
    POST with HTTP 403 while answering the SAME request WITH a UA — so the selector
    verified a host using headers this caller never sent. Rotate via the shared
    helper, and fail LOUDLY (raise) rather than returning None: `main()` already
    treats a None price as "refusing to plan off a stale number", and a silent None
    from a dead host is indistinguishable from a real answer of zero.
    """
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(__file__))
        if _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import rpc_call
        return rpc_call(method, params, timeout=45, tries=tries)
    except Exception:
        pass
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        RPC, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "gentech-treasury/1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("result")


def spot_price_sqrt(pool, dec_shift=1e12):
    """CL pool spot price token0->token1 via globalState().price (sqrtPriceX96)."""
    try:
        r = rpc("eth_call", [{"to": pool, "data": "0xe76c01e4"}, "latest"])
    except Exception:
        return None                 # an outage is NOT a price of zero
    if not r or r == "0x":
        return None
    sqrt_p = int(r[2:][0:64], 16)
    if sqrt_p == 0:
        return None
    return ((sqrt_p / 2**96) ** 2) * dec_shift


def price_history():
    """30d daily AVAX price series (for the rainbow momentum score)."""
    try:
        url = "https://coins.llama.fi/chart/avax:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7?span=30&period=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "GenTech-Steward/1.0"})
        with urllib.request.urlopen(req, timeout=45) as r:
            d = json.load(r)
        pts = d.get("coins", {}).get(
            "avax:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", {}).get("prices", [])
        return [p["price"] for p in pts]
    except Exception:
        return []


def rainbow_band(prices):
    """Coin PRICE rainbow score from 7d + 30d momentum (guide formula)."""
    if len(prices) < 8:
        return None, None, None
    now = prices[-1]
    p7 = prices[-8] if len(prices) > 8 else prices[0]
    p30 = prices[0]
    ch7 = (now / p7 - 1) * 100
    ch30 = (now / p30 - 1) * 100
    score = 0.6 * (ch7 / 10.0) + 0.4 * (ch30 / 10.0)
    score = max(-2.0, min(2.0, score))
    for name, lo, hi, action in BANDS:
        if lo <= score < hi:
            return {"band": name, "score": round(score, 2), "action": action,
                    "change_7d": round(ch7, 2), "change_30d": round(ch30, 2)}, ch7, ch30
    return None, ch7, ch30


BLACK_HEALTH = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/black-health.json"
BLACK_HEALTH_MAX_AGE_H = 12.0


def farm_apr():
    """Fee APR for our rail, from black-health.json — chain-measured AND age-gated.

    2026-09-27 FIX — this read the file with NO freshness check. A generator that only
    runs when something changes can leave a months-old fee APR in place, and a stale
    rate is indistinguishable from a live one once it is a bare number. The sibling
    reader (agentic-treasury-report) already refuses past 12h; this one now does too,
    and returns None instead of a frozen figure so the plan says "unavailable".
    """
    try:
        h = json.load(open(BLACK_HEALTH))
    except Exception:
        return None, None
    try:
        ts = h.get("ts")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
        if not isinstance(ts, (int, float)):
            return None, None                    # unstamped = cannot prove fresh = refuse
        if abs(ts) > 1e11:
            ts = ts / 1000.0
        age_h = (time.time() - ts) / 3600.0
        if age_h > BLACK_HEALTH_MAX_AGE_H:
            print(f"   ⚠️  black-health is {age_h:.1f}h old (gate "
                  f"{BLACK_HEALTH_MAX_AGE_H:.0f}h) — refusing a stale fee APR")
            return None, None
    except Exception:
        return None, None
    return h.get("yield_split", {}).get("fee_apr_pct"), h.get("pool", {}).get("tvl_usd")


def main():
    px = spot_price_sqrt(POOL)
    if not px:
        print("⚠️  AVAX price read failed — refusing to plan off a stale number")
        return 1
    hist = price_history()
    band, ch7, ch30 = rainbow_band(hist)
    fee_apr, tvl = farm_apr()

    deploy = 25.0   # reference deploy size (our historical position scale)
    rows = []
    for label, pct in LADDER:
        price = px * (1 + pct)
        tokens = deploy / price
        rows.append({"level": label, "price": round(price, 4),
                     "tokens_for_ref_deploy": round(tokens, 4)})
    base_tokens = rows[0]["tokens_for_ref_deploy"]
    for r in rows:
        r["token_advantage_pct"] = round((r["tokens_for_ref_deploy"] / base_tokens - 1) * 100, 2)
        # value if price RETURNS to current spot
        r["value_if_returns_to_spot"] = round(r["tokens_for_ref_deploy"] * px, 2)
        r["gain_vs_now"] = round(r["value_if_returns_to_spot"] - deploy, 2)
        # fee income on the SAME deployed dollars (APR is on deployed capital)
        r["fee_income_yr_same_apr"] = round(deploy * (fee_apr or 0) / 100, 2)

    out = {
        "when": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "ts": time.time(),
        "avax_usd_chain": round(px, 4),
        "price_rainbow": band,
        "yield_side": {
            "fee_apr_pct": fee_apr,
            "pool_tvl_usd": tvl,
            "note": ("fee APR is earned on DEPLOYED CAPITAL — a cheaper entry does "
                     "NOT raise the fee rate. See the honest_math field."),
        },
        "reference_deploy_usd": deploy,
        "ladder": rows,
        "honest_math": [
            "Fee APR is on deployed capital: $100 at $7.26 and $100 at $6.50 earn the SAME rate.",
            "What a cheaper entry buys: MORE TOKENS per dollar (see token_advantage_pct).",
            "Plus: less top-of-band risk, and fewer forced re-centers.",
            "Only a TVL-down/volume-up shift raises the APR itself — measured in black-health.json.",
        ],
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)

    print(f"🌈 RE-ENTRY YIELD PLAN — {out['when']}")
    print(f"   AVAX ${px:.4f} (chain) | 7d {ch7:+.1f}% | 30d {ch30:+.1f}%")
    if band:
        print(f"   PRICE RAINBOW: {band['band']} (score {band['score']:+}) — {band['action']}")
    print(f"   FARM FEE APR : {fee_apr}% on ${tvl:,.0f} TVL" if fee_apr else "   FARM FEE APR : unavailable")
    print()
    print(f"   {'level':<7}{'price':>9}{'tokens/$25':>12}{'vs now':>9}{'value if recovers':>19}")
    for r in rows:
        print(f"   {r['level']:<7}${r['price']:>8.4f}{r['tokens_for_ref_deploy']:>12.4f}"
              f"{r['token_advantage_pct']:>8.1f}%${r['value_if_returns_to_spot']:>18.2f}")
    print()
    print("   ⚠️  Fee APR does NOT rise from a cheaper entry — it is earned on")
    print("       deployed capital. Cheaper = more tokens + less top-of-range risk.")
    print(f"   wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
