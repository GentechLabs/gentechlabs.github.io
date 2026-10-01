#!/usr/bin/env python3
"""hold-yield-options.py — what can a HELD asset actually DO?

Jordan (2026-09-17): "the Fed chair and the council will know when is the best time to just
straight up hold a single asset or not... And is there anything interesting we could do with
holding?"

The question exposes a real gap in the HOLD mode I just built. HOLD as designed is FLAT: you
keep the token, you earn nothing, you wait. But "exiting the fee engine" and "earning nothing"
are NOT the same requirement — and the treasury already has a standing rule that says so:

    RESTAKE RULE (Jordan): "our new logic should be to restake if possible."

So this maps the real options for a held AVAX position, with live numbers rather than
suggestions. Categories:
  1. LIQUID STAKING   — keep the price exposure, earn the staking yield, stay liquid
  2. LENDING SUPPLY   — supply the asset, borrow against it, or just earn the supply rate
  3. SINGLE-SIDED LP  — back into a pool with one leg only (returns you to the fee engine)
  4. NOTHING          — hold raw. The honest baseline everything else must beat.
"""
from __future__ import annotations

import json
import sys
import urllib.request

UA = {"User-Agent": "GenTech-Steward/1.0 (treasury research)", "Accept": "application/json"}


def get(url: str):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=60))


def main() -> int:
    print("=" * 88)
    print("  WHAT A HELD AVAX POSITION CAN DO — live rates, not suggestions")
    print("=" * 88)

    try:
        pools = get("https://yields.llama.fi/pools")["data"]
    except Exception as e:                                            # noqa: BLE001
        print(f"  yields feed unavailable: {type(e).__name__}")
        return 1

    # ── 1. liquid staking on Avalanche ─────────────────────────────────────
    print("\n── 1. LIQUID STAKING (keep exposure, earn yield, stay liquid) ──")
    ls = [p for p in pools
          if p.get("chain") == "Avalanche"
          and any(k in (p.get("symbol") or "").upper()
                  for k in ("SAVAX", "STAVAX", "GGAVAX", "AVAX"))
          and any(k in (p.get("project") or "").lower()
                  for k in ("benqi", "ankr", "lido", "gojo", "stake"))
          and "AVAX" in (p.get("symbol") or "").upper()]
    ls.sort(key=lambda p: -(p.get("tvlUsd") or 0))
    if ls:
        print(f"   {'project':<20}{'pair':<20}{'TVL':>13}{'base APR':>10}{'reward':>9}")
        for p in ls[:8]:
            print(f"   {p.get('project','')[:19]:<20}{p.get('symbol','')[:19]:<20}"
                  f"{p.get('tvlUsd') or 0:>13,.0f}{p.get('apyBase') or 0:>9.2f}%"
                  f"{p.get('apyReward') or 0:>8.2f}%")
    else:
        print("   none found")

    # ── 2. lending supply ──────────────────────────────────────────────────
    print("\n── 2. LENDING — supply the held asset, earn while holding ──")
    lend = [p for p in pools
            if p.get("chain") == "Avalanche"
            and (p.get("symbol") or "").upper() in ("AVAX", "WAVAX", "SAVAX")
            and (p.get("project") or "").lower() in
                ("aave-v3", "benqi-lending", "aave-v2", "spark", "compound-v3", "euler-v2")]
    lend.sort(key=lambda p: -(p.get("apyBase") or 0))
    if lend:
        print(f"   {'project':<18}{'asset':<10}{'TVL':>13}{'supply APR':>12}")
        for p in lend[:8]:
            print(f"   {p.get('project','')[:17]:<18}{p.get('symbol','')[:9]:<10}"
                  f"{p.get('tvlUsd') or 0:>13,.0f}{p.get('apyBase') or 0:>11.2f}%")
    else:
        print("   none found")

    # ── 3. the honest comparison table ─────────────────────────────────────
    print("\n" + "=" * 88)
    print("  THE TRADE-OFF TABLE — what each option costs you")
    print("=" * 88)
    rows = [
        ("HOLD RAW",        "AVAX", "0%", "none", "none",
         "Baseline. Full exposure, full liquidity, zero yield."),
        ("LIQUID STAKE",    "sAVAX", "~5-7%", "staking validator/contract", "1-2 day unstake",
         "Exposure kept, yield earned, still liquid enough to trade. BEST FIT to the restake rule."),
        ("LEND SUPPLY",     "aAVAX", "see table", "lending market", "instant",
         "Modest yield, but unlocks BORROWING against it — the real option value."),
        ("SINGLE-SIDED LP", "LP", "fees", "pool + IL", "instant",
         "Returns you to the fee engine. Note this is no longer a HOLD — it is a re-entry."),
    ]
    print(f"   {'option':<18}{'asset':<8}{'yield':<10}{'risk adds':<28}{'exit liquidity'}")
    print("   " + "-" * 84)
    for o, a, y, r, liq, _ in rows:
        print(f"   {o:<18}{a:<8}{y:<10}{r:<28}{liq}")
    print()
    for o, a, y, r, liq, note in rows:
        print(f"   • {o}: {note}")

    print("\n" + "=" * 88)
    print("  🔶 THE INTERESTING ANSWER")
    print("=" * 88)
    print("  HOLD does not have to mean IDLE. 'Out of the fee engine' and 'earning nothing'")
    print("  are different requirements, and the restake rule says we should not conflate")
    print("  them: a held position can keep its exposure AND earn the staking yield.")
    print()
    print("  The genuinely interesting move is not the extra few percent. It is that")
    print("  LIQUID STAKING makes HOLD a YIELDING mode — which means the council's choice")
    print("  stops being 'farm (earn, take IL) vs hold (no earn, no IL)' and becomes a real")
    print("  3-way: farm fees / stake-and-hold / sit in stables.")
    print()
    print("  ⚠ And the counterweight: every one of these adds a CONTRACT to trust. We just")
    print("    declined Pharaoh for exactly that reason. A staking derivative is another")
    print("    unaudited-surface decision, and it should face the same venue review.")
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
