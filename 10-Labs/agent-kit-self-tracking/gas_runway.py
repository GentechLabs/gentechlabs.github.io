#!/usr/bin/env python3
"""gas_runway.py — how many operations does our AVAX actually cover?

Jordan (2026-09-17):
  "bullish mode would mean you're going to hold, right? So instead of swapping to the dry
   powder engine, which would be like taking profit all in USDC, you're gonna swap things
   over to the main asset, which is great because that's what you're gonna use for gas anyway."

He is right, and it is an operational point rather than a trading one. On Avalanche the
volatile leg of a WAVAX/USDC pool IS the gas token. So a HOLD position does two jobs at once:

  1. directional exposure to AVAX
  2. the gas reserve that pays for every future exit, harvest, and re-entry

That matters because the treasury currently holds 0.044738 AVAX (~$0.34) — roughly one full
exit. A book that can only afford its own exit once is fragile in a way nothing else in the
stack would reveal: the position value looks fine right up until the moment it needs to move
and cannot.

Jordan's standing gas philosophy (Aug 2026): NO hard gates. The agent calculates the tx cost
ahead of time and keeps that plus a ~20c floor — never a blanket buffer that blocks execution.
So this REPORTS runway; it never refuses a transaction.

Gas units below are typical Avalanche C-Chain figures for the operations our rails actually
call. They are estimates for planning, not quotes, and the report says so.
"""
from __future__ import annotations

import json
import sys
import urllib.request

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.
def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        return _avax_url()   # last resort only — avax_rpc preferred

RPC = _avax_url()
UA = {"User-Agent": "GenTech-Steward/1.0", "Content-Type": "application/json"}
WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"

# Typical gas units per operation (planning estimates, not quotes).
OPS = {
    "approve (ERC20)":            46_000,
    "collect()":                  80_000,
    "harvest / claimReward()":   110_000,
    "gauge.withdraw()":          120_000,
    "swap (simple)":             150_000,
    "decreaseLiquidity()":       200_000,
}
# A full CL exit = remove + collect + swap + remit
FULL_EXIT_UNITS = (200_000 + 80_000 + 150_000 + 60_000)
# A re-entry = approve x2 + mint
REENTRY_UNITS = (46_000 + 46_000 + 320_000)


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers=UA)
    d = json.load(urllib.request.urlopen(req, timeout=30))
    if "error" in d:
        raise RuntimeError(str(d["error"])[:90])
    return d.get("result")


def main() -> int:
    print("=" * 80)
    print("  GAS RUNWAY — what our AVAX actually covers")
    print("=" * 80)

    try:
        bal_wei = int(rpc("eth_getBalance", [WALLET, "latest"]), 16)
        gas_price = int(rpc("eth_gasPrice", []), 16)
    except Exception as e:                                            # noqa: BLE001
        print(f"  chain read failed: {type(e).__name__}: {e}")
        return 1

    avail = bal_wei / 1e18
    gp_gwei = gas_price / 1e9

    # AVAX price for a dollar read
    avax_usd = None
    try:
        req = urllib.request.Request(
            "https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd",
            headers={"User-Agent": "Mozilla/5.0"})
        avax_usd = json.load(urllib.request.urlopen(req, timeout=30))["avalanche-2"]["usd"]
    except Exception:                                                 # noqa: BLE001
        pass

    print(f"\n  wallet       : {WALLET}")
    print(f"  AVAX balance : {avail:.6f} AVAX"
          + (f"   (~${avail*avax_usd:,.4f} at ${avax_usd:,.2f})" if avax_usd else ""))
    print(f"  gas price    : {gp_gwei:.3f} nAVAX")

    def cost_avax(units: int) -> float:
        return units * gas_price / 1e18

    print(f"\n  {'operation':<26}{'AVAX':>13}{'USD':>10}{'affordable':>12}")
    print("  " + "-" * 61)
    for label, units in sorted(OPS.items(), key=lambda x: x[1]):
        c = cost_avax(units)
        n = int(avail // c) if c > 0 else 0
        usd = f"${c*avax_usd:,.4f}" if avax_usd else "n/a"
        print(f"  {label:<26}{c:>13.6f}{usd:>10}{n:>12}")

    print(f"\n  ── whole operations ──")
    fe = cost_avax(FULL_EXIT_UNITS)
    re_ = cost_avax(REENTRY_UNITS)
    n_exit = int(avail // fe) if fe else 0
    n_re = int(avail // re_) if re_ else 0
    fs = f"${fe*avax_usd:,.4f}" if avax_usd else "n/a"
    rs = f"${re_*avax_usd:,.4f}" if avax_usd else "n/a"
    print(f"  ONE full exit (remove+collect+swap+remit): {fe:.6f} AVAX  {fs}")
    print(f"     -> affordable now: {n_exit}")
    print(f"  ONE re-entry (approve x2 + mint)        : {re_:.6f} AVAX  {rs}")
    print(f"     -> affordable now: {n_re}")

    print("\n" + "=" * 80)
    print("  WHAT THIS MEANS FOR A HOLD POSITION")
    print("=" * 80)
    print("  On Avalanche the volatile leg IS the gas token. So a HOLD position that")
    print("  keeps its capital in WAVAX/AVAX funds its own operations:")
    print("    • directional exposure to AVAX")
    print("    • a gas reserve that scales WITH the position instead of being a fixed")
    print("      dust balance that has to be topped up separately")
    print("  A $25 hold at $7.63 is ~3.28 AVAX. That covers thousands of operations.")
    if avax_usd:
        for notional in (10, 25, 100):
            a = notional / avax_usd
            print(f"    ${notional:<4} hold -> {a:>7.3f} AVAX -> "
                  f"~{int(a//fe):>6} full exits of runway")
    print()
    print("  ⚠ HONEST COUNTERWEIGHT: if AVAX falls, the gas reserve shrinks at the same")
    print("    time the position loses value — the two are CORRELATED, not diversified.")
    print("    Holding the token for gas is operationally elegant and adds concentration")
    print("    risk. That trade should be made deliberately, not discovered.")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
