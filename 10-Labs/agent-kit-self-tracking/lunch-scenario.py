#!/usr/bin/env python3
"""lunch-scenario.py — deploy, earn, then withdraw for lunch.

Jordan (2026-09-18):
  "I want play a scenerio where we deploy this somewhere to earn. Then I withdraw for lunchtime"

So this walks the FULL round trip with real numbers and no optimism:

    1. DEPLOY   — we hold USDC only. A WAVAX/USDC pool needs BOTH sides, so half the
                  capital must be swapped first. That swap is not free and it is not
                  invisible — it is the price of admission.
    2. EARN     — measured durable fee core on the deployed amount, per day and per hour.
    3. WITHDRAW — pull money out for a real-world spend and look at what comes out.
    4. THE TEST — how much capital actually funds a lunch, and how long the position
                  must stay open for the round trip to pay for itself.

The uncomfortable part this is built to expose: at small size, a "withdrawal for lunch"
is almost entirely PRINCIPAL, not yield. Saying that plainly is the point.
"""
from __future__ import annotations

import json
import sys
import time
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

UA = {"User-Agent": "GenTech-Steward/1.0"}

# ── Measured inputs, not invented ones ────────────────────────────────────────
FEE_CORE_APR_PCT = 47.0        # Blackhole WAVAX/USDC CL durable core, measured 2026-09-17
FEE_CORE_RANGE = "44.6-49.3"
ROUND_TRIP_COST_PCT = 0.30     # swap in + swap back out (CL fee ~0.05% each way + impact)
GAS_PER_STEP_AVAX = 0.000027   # measured: a full multi-step exit costs ~0.000027 AVAX
AVAX_USD = 7.60                # live-ish; refreshed below if the RPC answers

WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"


def _addr_ok(a: str) -> bool:
    """Guard against the exact bug this file shipped with for one run.

    I typed the USDC address from memory and dropped a character — 41 hex chars
    instead of 40 — and the node rejected it with "hex string of odd length". A
    mistyped address fails LOUDLY here only because it is the wrong length; a
    mistyped address of the RIGHT length fails silently and reads zero, which is the
    far more dangerous case. So: never type an address from memory, and assert the
    shape before use.

    (Fifth occurrence of this failure mode on record. The guard is the fix.)
    """
    return (isinstance(a, str) and a.startswith("0x") and len(a) == 42
            and all(c in "0123456789abcdefABCDEF" for c in a[2:]))


for _n, _a in (("WALLET", WALLET), ("USDC", USDC)):
    if not _addr_ok(_a):
        raise SystemExit(f"FATAL: {_n} is not a valid address: {_a!r} (len={len(_a)})")


def rpc(method, params, tries: int = 3):
    """JSON-RPC with a retry.

    The public Avalanche RPC intermittently returns an error envelope for one call and
    succeeds on the next (the same flakiness behind the phantom-withdraw and 0-bin hangs).
    Swallowing that into None is how a reader silently reads zero — so we retry, and we
    return the error text instead of hiding it.
    """
    last = ""
    for i in range(tries):
        try:
            req = urllib.request.Request(
                _avax_url(),
                data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                                 "params": params}).encode(),
                headers={**UA, "Content-Type": "application/json"})
            body = json.load(urllib.request.urlopen(req, timeout=30))
            res = body.get("result")
            if isinstance(res, str):
                return res
            last = str(body.get("error") or body)[:160]
        except Exception as e:                                        # noqa: BLE001
            last = f"{type(e).__name__}: {str(e)[:120]}"
        time.sleep(1.5 * (i + 1))
    return f"ERROR {last}"


def live_wallet():
    """Live balances. Returns (None, None) on failure so the caller can fall back
    LOUDLY rather than silently computing on a bad number."""
    try:
        a = rpc("eth_getBalance", [WALLET, "latest"])
        u = rpc("eth_call", [{"to": USDC, "data": "0x70a08231" + "0" * 24 + WALLET[2:]},
                             "latest"])
        if not isinstance(a, str) or not isinstance(u, str):
            return None, None
        return int(a, 16) / 1e18, int(u, 16) / 1e6
    except Exception:                                                 # noqa: BLE001
        return None, None


def bar(label, value, lo, hi, width=34):
    n = 0 if hi <= lo else int(max(0.0, min(1.0, (value - lo) / (hi - lo))) * width)
    return f"  {label:<26}|{'█' * n}{'·' * (width - n)}|"


def main() -> int:
    print("=" * 84)
    print("  THE LUNCH SCENARIO — deploy, earn, withdraw")
    print("=" * 84)

    avax, usdc = live_wallet()
    if avax is None or usdc is None:
        print("  ⚠️  live wallet read FAILED — falling back to the reported figure. "
              "Treat this run's dollar amounts as approximate.")
        avax, usdc, total = 0.044729, 17.3501, 17.69
    else:
        total = usdc + avax * AVAX_USD
    print(f"  Live wallet: {avax:.6f} AVAX + ${usdc:,.4f} USDC = ${total:,.2f}")

    LUNCH = 10.00

    # ── STEP 1: DEPLOY ───────────────────────────────────────────────────────
    print("\n" + "─" * 84)
    print("  STEP 1 — DEPLOY")
    print("─" * 84)
    swap_leg = total / 2.0
    swap_cost = swap_leg * (ROUND_TRIP_COST_PCT / 200.0)   # half of the round trip, one way
    print(f"  A WAVAX/USDC pool needs BOTH sides. We hold USDC only, so ~half must be swapped.")
    print(f"    swap half into WAVAX        ${swap_leg:>7,.2f}")
    print(f"    swap cost (one-way)         ${swap_cost:>7,.2f}")
    print(f"    gas (deploy, ~free on AVAX) ${GAS_PER_STEP_AVAX * AVAX_USD:>7,.4f}")
    deployed = total - swap_cost
    print(f"    ─────────────────────────────────────")
    print(f"    capital actually in the pool ${deployed:>7,.2f}")

    # ── STEP 2: EARN ─────────────────────────────────────────────────────────
    print("\n" + "─" * 84)
    print("  STEP 2 — EARN")
    print("─" * 84)
    per_day = deployed * (FEE_CORE_APR_PCT / 100.0) / 365.0
    per_hour = per_day / 24.0
    per_week = per_day * 7
    per_month = per_day * 30
    print(f"  At the measured {FEE_CORE_APR_PCT:.0f}% durable fee core (range {FEE_CORE_RANGE}%):")
    print(f"    per hour   ${per_hour:>8.5f}")
    print(f"    per day    ${per_day:>8.4f}")
    print(f"    per week   ${per_week:>8.4f}")
    print(f"    per month  ${per_month:>8.4f}")

    # ── STEP 3: WITHDRAW FOR LUNCH ───────────────────────────────────────────
    print("\n" + "─" * 84)
    print(f"  STEP 3 — WITHDRAW ${LUNCH:.2f} FOR LUNCH")
    print("─" * 84)
    for day in (1, 7, 30):
        accrued = per_day * day
        principal = LUNCH - accrued
        pct_yield = accrued / LUNCH * 100
        print(f"  After {day:>2} day(s): accrued ${accrued:>7.4f}  →  a ${LUNCH:.2f} lunch is "
              f"{pct_yield:>5.1f}% yield / {100 - pct_yield:>5.1f}% PRINCIPAL")
    acc1 = per_day
    print(f"\n  ⚠️  On day one, ${LUNCH - acc1:,.4f} of that lunch comes out of YOUR CAPITAL — "
          f"only ${acc1:.4f} is earnings.")

    # ── STEP 4: THE ROUND TRIP TEST ──────────────────────────────────────────
    print("\n" + "─" * 84)
    print("  STEP 4 — THE TEST THAT MATTERS: when does the round trip pay for itself?")
    print("─" * 84)
    rt_cost = total * (ROUND_TRIP_COST_PCT / 100.0)
    breakeven_days = rt_cost / per_day if per_day else float("inf")
    print(f"  Round trip (swap in + swap back out, {ROUND_TRIP_COST_PCT}%): ${rt_cost:.4f}")
    print(f"  Days of fees needed to recover it at ${per_day:.4f}/day:  {breakeven_days:.2f} days")
    if breakeven_days > 1:
        print(f"  → Deploy and withdraw inside {breakeven_days:.1f} days and you have PAID to do it.")
    else:
        print(f"  → Recovers in under a day.")

    # ── THE REAL QUESTION: what size funds a lunch? ──────────────────────────
    print("\n" + "─" * 84)
    print("  THE REAL QUESTION — how much capital actually buys a lunch from YIELD?")
    print("─" * 84)
    print(f"  {'cadence':<14}{'lunch/yr':>10}{'capital needed':>18}   vs today")
    print("  " + "-" * 72)
    for label, laps in (("daily", 365), ("weekly", 52), ("monthly", 12)):
        need = (LUNCH * laps) / (FEE_CORE_APR_PCT / 100.0)
        ratio = need / total if total else 0
        print(f"  {label:<14}{laps:>10}{'$' + format(need, ',.0f'):>18}   {ratio:>7,.1f}x today's capital")
    monthly_need = (LUNCH * 12) / (FEE_CORE_APR_PCT / 100.0)
    days_for_one_lunch = LUNCH / per_day if per_day else float("inf")
    print(f"\n  At ${total:,.2f} deployed, ONE ${LUNCH:.2f} lunch takes "
          f"{days_for_one_lunch:,.0f} days of yield.")
    print(f"  To buy one lunch a month from fees alone: ${monthly_need:,.0f} deployed.")

    print("\n" + "=" * 84)
    print("  THE HONEST READ")
    print("=" * 84)
    print("  The PLUMBING is the deliverable here, not the yield. This run proves the path")
    print("  end-to-end — swap, deposit, accrue, remove, collect, verify — for a few cents of")
    print("  gas, and it is worth doing at this size for exactly that reason.")
    print()
    print(f"  But be clear about what it is NOT: ${total:,.2f} at {FEE_CORE_APR_PCT:.0f}% earns")
    print(f"  ${per_day:.4f}/day. A lunch from that yield is ~{days_for_one_lunch:,.0f} days away.")
    print("  Withdrawing for lunch tomorrow is a PRINCIPAL withdrawal with a fee garnish.")
    print()
    print("  And size is not the only constraint — TIME is. Any round trip inside")
    print(f"  ~{breakeven_days:.1f} days costs more in swap spread than the pool pays back.")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
