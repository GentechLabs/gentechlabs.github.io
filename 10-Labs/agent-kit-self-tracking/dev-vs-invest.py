#!/usr/bin/env python3
"""
dev-vs-invest.py — DEV quality and INVEST quality are SEPARATE AXES.

Jordan (2026-09-19): "if Development with Algorand is beneficial, but not investment,
that's fine. We should add a Section... developers want to be investors... now developers
have to separate themselves... I have to separate working on projects versus investing
in projects, two different things."

WHY THIS EXISTS: a token can be excellent to BUILD with and terrible to HOLD. Judging one by
the other is how you end up buying a chain because its docs are nice, or dismissing a chain
because its token chart is ugly. The two questions have different inputs and different answers.

  DEV    = can we BUILD here?  cost to transact, ecosystem depth, tooling, composability
  INVEST = does HOLDING pay?   price trend, measured yield rails, liquidity to exit

A DISAGREEMENT IS A RESULT, NOT AN ERROR. It is the whole point of the section.
"""
import json, urllib.request, time

UA = {"User-Agent": "GenTech-Steward/1.0"}

def get(url, timeout=25):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
        return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, f"{type(e).__name__}: {str(e)[:90]}"

# ── INVEST axis: measured price trend (Coinbase, keyless) ────────────────────
def price_trend(pair):
    """Page Coinbase candles — a single call caps at 300, which silently truncated
    our 365d window to 'no data' and made every verdict read as a decline.
    A MISSING VALUE IS NOT A NEGATIVE READING."""
    all_c = {}
    end = None
    for _ in range(5):                       # 5 x 300 = 1500 days, plenty
        url = f"https://api.exchange.coinbase.com/products/{pair}/candles?granularity=86400"
        if end:
            url += f"&end={end}"
        st, body = get(url)
        if st != 200:
            break
        try:
            chunk = json.loads(body)
        except Exception:
            break
        if not chunk:
            break
        for r in chunk:
            all_c[r[0]] = r[4]
        oldest = min(r[0] for r in chunk)
        if end and oldest >= end:
            break
        end = oldest - 86400
        if len(chunk) < 300:
            break
        time.sleep(0.2)
    if len(all_c) < 30:
        return None
    cl = [all_c[k] for k in sorted(all_c)]
    def chg(n):
        if len(cl) <= n:
            return None                      # UNKNOWN, not zero
        return (cl[-1] / cl[-1 - n] - 1) * 100
    hi = max(cl[-365:]) if len(cl) >= 365 else max(cl)
    return {"now": cl[-1], "d30": chg(30), "d90": chg(90), "d365": chg(365),
            "days": len(cl), "from_high": (cl[-1] / hi - 1) * 100}

# ── INVEST axis: measured yield rails (our own prior chain work) ─────────────
# rail_class comes from the buy list work: FARM = real fee LP; STAKE = staking/RWA;
# HOLD_ONLY = no measured on-chain yield. Source: steward-buylist.py.
RAIL = {
    "AVAX": ("FARM",  "LFJ Joe v2.2 bs10 — chain-measured 7.85-16.95%, fee-only"),
    "ETH":  ("FARM",  "WETH.e/WAVAX Uni v3 0.05% — chain-measured, fee-only"),
    "SOL":  ("STAKE", "liquid staking 4.78-6.00% (JitoSOL/JupSOL/mSOL)"),
    "TAO":  ("FARM",  "WTAO-USDC 104.9% reported (aggregator-tier)"),
    # LINK CORRECTED 2026-09-28. The old note said "ETHEREUM ONLY — no Avalanche rail". That is
    # true of OUR tooling, not of the chain: LFJ/Blackhole genuinely has no LINK.e pool (verified
    # on-chain — factory.poolByPair(LINK.e, WAVAX|USDC|USDT) all return 0x0), BUT Avalanche
    # carries real LINK.e liquidity on Uniswap V3 (LINK.e/WAVAX, ~$91K TVL, 106.9% in-range APR on
    # a $1.4K in-range base; LINK.e/USDC ~$36K). So farming LINK on Avalanche is possible on a
    # venue we have NOT wired. Ethereum ETH-LINK v4 remains the deeper rail.
    "LINK": ("FARM",  "Avalanche: Uniswap V3 LINK.e/WAVAX ~$91K TVL (106.9% in-range, NOT yet wired); no LFJ pool. Deepest: ETH-LINK v4 ~62.8%"),
    # ONDO RESTORED 2026-09-29 as TRADE, not STAKE. The old entry read ("STAKE", "USDY 3.58%") —
    # STAKE was wrong (there is no stakeable reachable asset) and USDY is a DIFFERENT TOKEN. What
    # exists is a long/short rail: Orderly's PERP_ONDO_USDC on Avalanche, native USDC, no bridge.
    "ONDO": ("TRADE", "Orderly PERP_ONDO_USDC on Avalanche (10x, $10 min) — the token is Ethereum-only, the perp is reachable"),
    "BTC":  ("HOLD_ONLY", "every high-TVL BTC pool reads 0.00%"),
    "COQ":  ("HOLD_ONLY", "$50K/day volume — cannot exit size"),
    "ALGO": ("HOLD_ONLY", "7 pools total; staking 4.87% gated behind 30K ALGO (~$2,937)"),
    "XAUT": ("HOLD_ONLY", "no rail"),
}

PAIRS = {"BTC":"BTC-USD","ETH":"ETH-USD","SOL":"SOL-USD","AVAX":"AVAX-USD",
         "LINK":"LINK-USD","TAO":"TAO-USD","ALGO":"ALGO-USD","ONDO":"ONDO-USD"}

print("=" * 100)
print("  DEV vs INVEST — TWO AXES, MEASURED SEPARATELY")
print("=" * 100)
print()
print("  DEV  = can we BUILD here?   (cost, depth, tooling)")
print("  INVEST = does HOLDING pay?  (trend, measured yield, exit liquidity)")
print()
print(f"  {'ASSET':<7}{'30d':>9}{'90d':>9}{'365d':>9}{'from high':>11}   {'RAIL':<10}{'INVEST VERDICT'}")
print("  " + "-" * 96)

data = {}
for name, pair in PAIRS.items():
    t = price_trend(pair)
    if not t:
        print(f"  {name:<7}  (no candle data)")
        continue
    rc, note = RAIL.get(name, ("?", ""))
    # INVEST verdict: trend must be up AND a rail must exist to be a real holding case
    # A MISSING VALUE IS NOT A NEGATIVE. `(x or 0) > 0` silently turned "no 365d data"
    # into "365d down" on every asset — the same null->zero bug as the regime classifier.
    up30 = t["d30"] is not None and t["d30"] > 0
    y365 = t["d365"]
    y365_txt = "365d UNKNOWN" if y365 is None else ("365d UP" if y365 > 0 else "365d DOWN")
    if rc == "HOLD_ONLY":
        verdict = "PRICE BET ONLY" if up30 else "WEAK"
    elif up30:
        verdict = f"EARNS · {y365_txt}"
    else:
        verdict = f"EARNS · NO TREND · {y365_txt}"
    data[name] = {"trend": t, "rail": rc, "rail_note": note, "verdict": verdict}
    f = lambda v: f"{v:+.1f}%" if v is not None else "   n/a"
    print(f"  {name:<7}{f(t['d30']):>9}{f(t['d90']):>9}{f(t['d365']):>9}"
          f"{t['from_high']:>10.1f}%   {rc:<10}{verdict}")

print()
print("=" * 100)
print("  WHERE THE TWO AXES DISAGREE — this is the whole point")
print("=" * 100)

DEV = {
    "AVAX": ("STRONG",  "our home chain; ~$0.0002/tx measured; LFJ+Uni+Blackhole depth; RWA inflow live"),
    "ETH":  ("STRONG",  "deepest ecosystem; but Ethereum L1 gas is the cost, not the asset"),
    "SOL":  ("STRONG",  "fast, cheap, mature tooling; Meteora/Jupiter rails"),
    "ALGO": ("MODERATE","clean tech, quantum-resistant narrative; thin DeFi, few builders"),
    "COQ":  ("N/A",     "a memecoin — nothing to build ON, only to trade"),
    "BTC":  ("WEAK",    "not a build target; no contract layer we use"),
    "LINK": ("MODERATE","oracle infra is real, but we consume it, we don't build on it"),
    "TAO":  ("MODERATE","AI-subnet thesis; dev surface is Bittensor-native"),
}
print()
print(f"  {'ASSET':<7}{'DEV':<11}{'INVEST':<20}DISAGREEMENT")
print("  " + "-" * 96)
for name, d in data.items():
    dev, devnote = DEV.get(name, ("?", ""))
    inv = d["verdict"]
    dev_good = dev in ("STRONG", "MODERATE")
    inv_good = inv.startswith("EARNS") and "365d DOWN" not in inv
    flag = ""
    if dev_good and not inv_good:
        flag = "⚠️ BUILD YES / HOLD NO"
    elif inv_good and not dev_good:
        flag = "⚠️ HOLD YES / BUILD NO"
    else:
        flag = "· aligned"
    print(f"  {name:<7}{dev:<11}{inv:<20}{flag}")

print()
print("  ALGO is the canonical case Jordan named: MODERATE dev, HOLD_ONLY invest.")
print("  Building on Algorand costs us little. Holding it pays us nothing.")
print("  Those are different questions, and answering one does not answer the other.")
