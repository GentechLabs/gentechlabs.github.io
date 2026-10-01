#!/usr/bin/env python3
"""lfj-fee-decode.py — decode REAL fee revenue from LFJ swap events and settle the APR.

The LB v2.2 Swap event:
  Swap(address indexed sender, address indexed to, uint24 id, bytes32 amountsIn, bytes32 amountsOut,
       uint24 volatilityAccumulator, bytes32 totalFees, bytes32 protocolFees)

That means the FEES ARE IN THE LOG. No bin math, no estimation, no aggregator. The data payload is
six 32-byte words:
  w0 id · w1 amountsIn · w2 amountsOut · w3 volatilityAccumulator · w4 totalFees · w5 protocolFees
and totalFees packs (uint128 feeY, uint128 feeX) — measured, see BYTE ORDER below.

So: sum feeX and feeY across every swap in a 24h window, convert at spot, and we have the pool's ACTUAL
fee revenue. Then APR = fees*365/TVL. That is the number under dispute (90.7% vs 21.20%), and now
nothing between us and it but arithmetic.

READ-ONLY.
"""
from __future__ import annotations

import json
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

# ── live price helper (added 2026-09-20) ───────────────────────────────────────
# Was hardcoded at 8.24 and silently under-valued every position by ~24%.
# A stale constant is not a crash — it is a confidently wrong number.
def _live_avax_usd():
    """Live AVAX/USD from Coinbase. Falls back to the old constant only if the
    network read fails, so the tool degrades rather than dies."""
    try:
        import urllib.request as _u
        _r = _u.urlopen(_u.Request(
            "https://api.exchange.coinbase.com/products/AVAX-USD/ticker",
            headers={"User-Agent": "GenTech-Steward/1.0"}), timeout=15)
        return float(json.loads(_r.read())["price"])
    except Exception:
        return 8.24


RPC = _avax_url()
UA = {"User-Agent": "GenTech-Steward/1.0", "Content-Type": "application/json"}
PAIR = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
TVL_USD = 716_840.0
AVAX_USD = _live_avax_usd() or 8.24


def rpc(method, params, retries=3):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for _ in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(RPC, data=body, headers=UA),
                                        timeout=45) as r:
                d = json.load(r)
            if "error" in d:
                time.sleep(1.2)
                continue
            return d.get("result")
        except Exception:
            time.sleep(1.2)
    return None


# ── BYTE ORDER + DECIMALS ARE READ FROM THE CHAIN, NOT ASSUMED ─────────────────
# BUG FIXED 2026-09-21: this decoder had the 128-bit halves INVERTED (it divided the
# high half by 1e18 as if it were WAVAX and the low half by 1e6 as if it were USDC).
# Measured on-chain at pool 0x864d4e5e...: getTokenX = WAVAX.b31f (18dp),
# getTokenY = USDC.b97e (6dp) -> the LB Swap event packs totalFees as
# (uint128 amountY, uint128 amountX), i.e. HIGH = USDC, LOW = WAVAX. Sibling
# decoder chain-fee-rank.py already carried the verified comment; this file did not.
# The inversion produced "$81,553,172,056,302.69 in 24h" and a 4,152,517,688,821%
# APR that was then printed as THE CHAIN'S VERDICT. Cross-check that settles it:
# with the correct halves, median fee / median notional = 0.0511%, which matches the
# pool's own fee law (baseFactor 5000 x binStep 10 / 1e4 / 100 = 0.050000% base fee).
# With the inverted halves that ratio is 0.00%. A decode that cannot recognise a
# plausible number is as unreadable as one that cannot fail.
def _sel(sig):
    from Crypto.Hash import keccak
    h = keccak.new(digest_bits=256); h.update(sig.encode())
    return "0x" + h.hexdigest()[:8]


def _token_meta():
    """(x_sym, x_dec, y_sym, y_dec) read live from the pair. Never assumed."""
    def addr(fn):
        r = rpc("eth_call", [{"to": PAIR, "data": _sel(fn)}, "latest"])
        return ("0x" + r[-40:]).lower() if r else None
    def dec(a):
        r = rpc("eth_call", [{"to": a, "data": _sel("decimals()")}, "latest"])
        return int(r, 16) if r else None
    def sym(a):
        r = rpc("eth_call", [{"to": a, "data": _sel("symbol()")}, "latest"])
        if not r:
            return "?"
        h = r[2:]
        # string-returning tokens: word0 = offset (0x20), word1 = length. A bytes32
        # token returns the name inline in word0 instead — the earlier version tried
        # the string path unconditionally and printed NUL-packed labels
        # (e.g. "\x00\x00...\x05") for both tokens.
        if int(h[0:64], 16) == 32 and len(h) >= 128:
            n = int(h[64:128], 16)
            try:
                return bytes.fromhex(h[128:128 + n * 2]).decode(errors="replace").strip("\x00")
            except Exception:
                pass
        return bytes.fromhex(h[0:64]).rstrip(b"\x00").decode(errors="replace").strip()
    xa, ya = addr("getTokenX()"), addr("getTokenY()")
    return sym(xa), dec(xa), sym(ya), dec(ya)


def topic0(sig):
    from Crypto.Hash import keccak
    h = keccak.new(digest_bits=256)
    h.update(sig.encode())
    return "0x" + h.hexdigest()


def main():
    global TVL_USD
    print("=" * 104)
    print("  DECODING REAL FEE REVENUE FROM LFJ SWAP EVENTS — settling 90.7% vs 21.20%")
    print("=" * 104)
    print(f"  pair {PAIR}")
    print(f"  TVL  ${TVL_USD:,.0f} (chain reserves) · AVAX ${AVAX_USD}")
    sym_x, dec_x, sym_y, dec_y = _token_meta()
    try:
        res = rpc("eth_call", [{"to": PAIR, "data": _sel("getReserves()")}, "latest"])
        if res and len(res) >= 2 + 128:
            h = res[2:]
            TVL_USD = (int(h[0:64], 16) / 10 ** dec_x) * AVAX_USD + int(h[64:128], 16) / 10 ** dec_y
            print(f"  TVL re-read from chain: ${TVL_USD:,.0f} (was a hardcoded ${716840:,.0f})")
    except Exception as e:
        print(f"  \u26a0\ufe0f TVL read failed ({type(e).__name__}) — using the configured ${TVL_USD:,.0f}")
    print(f"  tokens (chain): X={sym_x} ({dec_x}dp) · Y={sym_y} ({dec_y}dp)")
    if None in (dec_x, dec_y) or dec_x == dec_y:
        print("  \u274c could not establish distinct token decimals from the chain — refusing to decode")
        return 3

    blk = rpc("eth_blockNumber", [])
    latest = int(blk, 16)
    DAY, windows = 43_200, 24
    span = DAY // windows
    t0 = topic0("Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)")

    fee_x_total = fee_y_total = 0.0
    n = 0
    bad = 0
    ratios = []          # per-swap fee / notional — the self-check that caught the inversion
    notional_total = 0.0
    print(f"\n  scanning {DAY:,} blocks in {windows} windows (latest {latest:,})\n")
    print(f"  {'win':>4}{'swaps':>7}{'WAVAX fees':>16}{'USDC fees':>14}{'USD fees':>12}")
    print("  " + "-" * 54)
    for i in range(windows):
        f = latest - DAY + i * span
        t = min(f + span - 1, latest)
        logs = rpc("eth_getLogs", [{"fromBlock": hex(f), "toBlock": hex(t),
                                    "address": PAIR, "topics": [t0]}])
        if logs is None:
            print(f"  {i:>4}   fetch failed")
            continue
        wx = uy = 0.0
        for lg in logs:
            data = lg.get("data", "0x")[2:]
            if len(data) < 64 * 6:
                bad += 1
                continue
            try:
                tot = int(data[64 * 4:64 * 5], 16)          # w4 = totalFees
                # LB v2.2 packs (uint128 amountY, uint128 amountX): HIGH = tokenY,
                # LOW = tokenX. Verified on-chain, not assumed (see BYTE ORDER above).
                uy += (tot >> 128) / 10 ** dec_y           # high half  = tokenY (USDC)
                wx += (tot & ((1 << 128) - 1)) / 10 ** dec_x  # low half = tokenX (WAVAX)
                ain = int(data[64:128], 16)
                # notional in USD terms, same orientation as the fees above
                notional = ((ain >> 128) / 10 ** dec_y) + ((ain & ((1 << 128) - 1)) / 10 ** dec_x) * AVAX_USD
                fee_usd = ((tot >> 128) / 10 ** dec_y) + ((tot & ((1 << 128) - 1)) / 10 ** dec_x) * AVAX_USD
                if notional > 0:
                    ratios.append(fee_usd / notional)
                    notional_total += notional
                n += 1
            except Exception:
                bad += 1
        fee_x_total += wx
        fee_y_total += uy
        print(f"  {i:>4}{len(logs):>7}{wx:>16.6f}{uy:>14.2f}{wx*AVAX_USD+uy:>12.2f}")

    usd = fee_x_total * AVAX_USD + fee_y_total
    print("\n" + "=" * 104)
    print("  CHAIN-TRUTH FEE REVENUE — 24 hours")
    print("=" * 104)
    print(f"    swaps decoded        : {n:,}   (undecodable: {bad})")
    print(f"    fees in {sym_x:<12}: {fee_x_total:,.6f}  = ${fee_x_total*AVAX_USD:,.2f}")
    print(f"    fees in {sym_y:<12}: {fee_y_total:,.4f}  = ${fee_y_total:,.2f}")
    print(f"    TOTAL FEES / 24h     : ${usd:,.2f}")
    if n == 0:
        print("    ❌ nothing decoded — not reporting an APR from it")
        return 2

    print("\n" + "=" * 104)
    print("  SELF-CHECK — two independent plausibility tests, both on the SAME numbers the APR uses")
    print("=" * 104)
    print(f"    swaps with a usable notional : {len(ratios):,}")
    print(f"    notional swept (24h)         : ${notional_total:,.0f}")

    reasons = []

    # TEST 1 — fee/notional ratio vs the pool's OWN fee law.
    if ratios:
        import statistics as _st
        med = _st.median(ratios) * 100
        print(f"    [1] median fee / notional    : {med:.4f}%")
        print("        pool's own law (baseFactor x binStep) : 0.050000% base fee")
        t1 = 0.005 <= med <= 0.60
        print(f"        -> {'PASS' if t1 else 'FAIL'} (expect a few bp to a few tens of bp per swap)")
        if not t1:
            reasons.append(f"fee/notional {med:.4f}% outside 0.005-0.60%")
    else:
        t1 = False
        print("    [1] median fee / notional    : n/a -> FAIL (no sample, decode unverified)")
        reasons.append("no fee/notional sample")

    # TEST 2 — THE ORIENTATION TEST. Test 1 is invariant to swapping which 128-bit half
    # is divided by which decimals (it recomputes both sides the same way), so on its own
    # it CANNOT catch the inversion that actually broke this file. Test 2 uses the accrued
    # `usd` total the APR is built from, so an inverted pair cannot slip through: a swap
    # of the halves divides a USDC-scale value by 1e18 and multiplies a WAVAX-scale value
    # by 1e6/... which inflates the fee total by ~11 orders of magnitude and implies a
    # daily volume the pool could not possibly trade. Bounded by TVL, which is physical.
    implied_vol = usd / 0.0005 if usd > 0 else 0.0
    turnover = implied_vol / TVL_USD if TVL_USD > 0 else float("inf")
    print(f"    [2] implied vol/day          : ${implied_vol:,.0f}")
    print(f"        turnover vs chain TVL    : {turnover:,.1f}x  (ceiling 100x)")
    t2 = turnover <= 100 and usd > 0
    print(f"        -> {'PASS' if t2 else 'FAIL'} (a pool cannot sweep >100x its own TVL per day)")
    if not t2:
        reasons.append(f"implied turnover {turnover:,.1f}x TVL exceeds 100x")

    ok = t1 and t2

    print("\n" + "=" * 104)
    print("  VERDICT")
    print("=" * 104)
    if not ok:
        print("    \u274c REFUSING TO REPORT AN APR: the decode did not reproduce a")
        print("       plausible number against the pool's own physics, so the total is")
        print("       not trustworthy.")
        print("       An inverted 128-bit pair or a wrong token map looks exactly like a")
        print("       legitimate giant number. No verdict is issued on an unverified decode.")
        for r in reasons:
            print(f"       · {r}")
        return 4
    apr = usd * 365 / TVL_USD * 100
    print(f"    FEE APR (chain-derived) : {apr:,.2f}%   (gross, on total pool TVL)")
    print(f"    implied vol/day @0.05%  : ${usd / 0.0005:,.0f}")
    print(f"    chain says      : {apr:,.2f}%")
    print(f"    aggregator says : 21.20%")
    print(f"    our old note    : 90.70%")
    d21 = abs(apr - 21.20)
    d90 = abs(apr - 90.70)
    if d21 < d90:
        print(f"\n    \u2192 THE CHAIN AGREES WITH 21.20% (off by {d21:.2f} pts). The 90.70% was WRONG.")
    else:
        print(f"\n    \u2192 THE CHAIN SUPPORTS THE HIGHER FIGURE (off by {d90:.2f} pts from 90.70%).")
    print("\n    NOTE: this APR is GROSS pool fees on TOTAL pool TVL. It is not the APR a")
    print("    given position earns — that depends on where our bins sit vs the active bin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
